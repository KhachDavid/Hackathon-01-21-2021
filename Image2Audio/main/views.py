from django.shortcuts import render
from image.forms import NewImageForm
from image.models import NewImage
from spotify.SpotifyAPI import SpotifyAPI, embedify
import requests, random
from .keywords import get_keywords_from_image, get_emotion_from_url

ClientID = '86e250ea3ec64541809ce9c138550641'
ClientSecret = 'dcc696c7c934482a9d7f47d03a9a841a'
client = SpotifyAPI(ClientID, ClientSecret)

def home(request):
    if request.method == 'POST':
        image_form = NewImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            image = image_form.cleaned_data['image']
            image_form.save()
            # p = NewImage.objects.get(image=image_form.cleaned_data['image'])
            keywords = get_keywords_from_image(f"images/{image.name}")
            
            list_of_playlists = []
            
            for keyword in keywords:
                spotify_search = client.search(keyword)

                playlist_link = ""
                try:
                    playlist_link = spotify_search['playlists']['items'][0]['external_urls']['spotify']
                    playlist_link = embedify(playlist_link)
                    list_of_playlists.append(playlist_link)
                except IndexError:
                    pass
                
                # for item in spotify_search['playlists']['items']:
                #    playlist_link = item['external_urls']['spotify']
                #    playlist_link = embedify(playlist_link)
                #    list_of_playlists.append(playlist_link)

            # emotion_list = get_emotion_from_url(f"images/{image.name}", 3)
            # print(emotion_list)

            context = {
                'list_of_playlists': list_of_playlists
            }
            print(playlist_link)
            return render(request, 'main/home.html', context)
            # return redirect('profile')

    else:
        image_form = NewImageForm()
    context = {
        'image_form': image_form
    }

    return render(request, 'main/home.html', context)


def login(request):
    return render(request, 'main/login.html')
