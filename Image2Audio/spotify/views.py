from django.shortcuts import render, redirect, HttpResponse
from .SpotifyAPI import SpotifyAPI, embedify
import json, requests, random
from image.forms import NewImageForm
from image.models import NewImage
from main.keywords import get_keywords_from_image
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

    # Obtain Top Artists
    # artists = client.get_users_top_artists(num_entities=10)
    # audio_features['audio_features'][0]['danceability']
    # audio_features['audio_features'][0]['energy']
    request.session['authorization_header'] = authorization_header

    image_form = NewImageForm()
    context= {
        'image_form': image_form,
        'bool': False
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
            spotify_play = client.create_playlist(authorization_header, playlist_tracks, image.name)
            spotify_play = embedify(spotify_play)

            context = {
                'list_of_playlists': spotify_play,
                'bool': True
            }
            # print(playlist_link)
            return render(request, 'main/home.html', context)
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )