from django.shortcuts import render, redirect, HttpResponse
from .SpotifyAPI import SpotifyAPI, embedify
import json, requests, random
from image.forms import NewImageForm
from image.models import NewImage
from main.keywords import get_keywords_from_image, get_emotion_from_url, get_emotion_from_image
import text2emotion as te
from collections import OrderedDict


ClientID = '86e250ea3ec64541809ce9c138550641'
ClientSecret = 'dcc696c7c934482a9d7f47d03a9a841a'
client = SpotifyAPI(ClientID, ClientSecret)

SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/callback".format(CLIENT_SIDE_URL, PORT)

def auth(request):
    return redirect(client.generate_auth_url())

def callback(request):

    client.set_show_dialog_false()
    client.empty_the_tracks()

    # Authorization
    auth_token = request.GET.get('code')
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': ClientID,
        'client_secret': ClientSecret,
    }

    post_request = requests.post(client.get_token_url(), data=code_payload)
        
    # Tokens are Returned to Application
    flag = False
    while not flag:
        try:
            response_data = json.loads(post_request.text)
            flag = True
        except json.decoder.JSONDecodeError:
            pass
    
    try:
        access_token = response_data["access_token"]
    except KeyError:
        return redirect('/auth')
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    try:
        profile_data = json.loads(profile_response.text)
    except json.decoder.JSONDecodeError:
        pass
    
    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    try:
        playlist_data = json.loads(playlists_response.text)
    except json.decoder.JSONDecodeError:
        context= {
            'prof_pic': "/static/musicplayer/wine.png",
            'random_track': 'https://open.spotify.com/embed/track/2g8HN35AnVGIk7B8yMucww',
            'users_name': 'Dashboard',
        }
        return render(request, "main/spotify.html", context)

    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]

    # Get tracks
    list_of_songs = []
    flag = False
    while not flag:
        try:
            for n in range(1, len(display_arr)):
                playlist_id = display_arr[n]['id']
                tracks_response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                                            headers=authorization_header)
                try:
                    tracks_data = json.loads(tracks_response.text)
                except json.decoder.JSONDecodeError:
                    pass
                list_of_songs.append(tracks_data)
            flag = True
        except json.decoder.JSONDecodeError:
            pass

    # Profile Picture and Name
    users_name = display_arr[0]['display_name']
    try:
        prof_pic = display_arr[0]['images'][0]['url']
    except:
        prof_pic = "/static/musicplayer/wine.png"

    # Get Audio Features
    tracks = []
    for i in range(len(list_of_songs)):
        for track in list_of_songs[i]['items']:        
            try:
                # print(track['track']['id'])
                tracks.append(track['track']['id'])
            except TypeError:
                pass

    print(f"There are {len(tracks)} songs")
    audio_features = []
    len_of_songs = len(tracks)

    # Obtain Audio Features For the Songs
    if len(tracks) <= 100:
        audio_features = client.get_audio_features(auth_header=authorization_header, track_ids=tracks)
    else:
        while (len_of_songs > 0):
            flag = False
            while not flag:
                try:
                    audio_features_index = client.get_audio_features(auth_header=authorization_header, track_ids=tracks[len_of_songs - 100:] if len_of_songs > 100 else tracks[:len_of_songs])
                    audio_features.append(audio_features_index)
                    len_of_songs = len_of_songs - 100
                    flag = True
                except json.decoder.JSONDecodeError:
                    pass

    # Obtain Top Artists
    # artists = client.get_users_top_artists(num_entities=10)
    # audio_features['audio_features'][0]['danceability']
    # audio_features['audio_features'][0]['energy']
    request.session['authorization_header'] = authorization_header
    request.session['audio_features'] = audio_features
    image_form = NewImageForm()
    context= {
        'prof_pic': prof_pic,
        'users_name': users_name,
        'image_form': image_form
    }
    return render(request, "main/home.html", context)


def update_the_song(request):
    #if request.method == 'POST':
     #   sad_or_happy = request.POST.get('sad_or_happy')
      #  dance_or_no = request.POST.get('dance_or_no')
       # tired_or_not = request.POST.get('tired_or_not')
      #  alone_or_not = request.POST.get('alone_or_not')
     #   request.session['sad_or_happy'] = sad_or_happy
    #    request.session['alone_or_not'] = alone_or_not
    #    request.session['dance_or_no'] = dance_or_no
    #    request.session['tired_or_not'] = tired_or_not
    
    if request.method == 'POST':
        authorization_header = request.session.get('authorization_header')
        print(1)
        image_form = NewImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            image = image_form.cleaned_data['image']
            image_form.save()
            # p = NewImage.objects.get(image=image_form.cleaned_data['image'])
            keywords = get_keywords_from_image(f"images/{image.name}")
            list_of_playlists = []
            print(keywords)
            
            keywstr = ""
            for element in keywords:
                keywstr += element + " "

            top_artists = client.get_users_top_artists(authorization_header, 50)
            artists = client.get_related_artists(authorization_header, top_artists)
            tracks = client.get_top_tracks(authorization_header, artists)
            cluster = client.cluster_ids(tracks)
            
            # Get the mood
            emotion_dump1 = te.get_emotion(keywstr)
            print(emotion_dump1)

            one = max(emotion_dump1['Happy'], emotion_dump1['Happy'])
            two = max(emotion_dump1['Angry'], emotion_dump1['Surprise'], emotion_dump1['Fear'])

            mood = (one + two) / 2

            user_tracks = client.add_and_get_user_tracks(authorization_header, cluster)
            audio_feat = client.standardize_audio_features(user_tracks)
            playlist_tracks = client.select_tracks(audio_feat, float(mood))
            spotify_play = client.create_playlist(authorization_header, playlist_tracks, 'Image Playlist')
            spotify_play = embedify(spotify_play)
            context = {
                'list_of_playlists': spotify_play,
            }
            # print(playlist_link)
            return render(request, 'main/home.html', context)
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )