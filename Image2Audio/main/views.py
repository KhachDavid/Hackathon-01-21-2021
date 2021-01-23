from django.shortcuts import render
from image.forms import NewImageForm
from image.models import NewImage
from spotify.SpotifyAPI import SpotifyAPI, embedify
import requests, random

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
            
            # https://labs.everypixel.com/api/docs
            client_id = 'J93dlmnXh0XusKixhnpz4K3z'
            client_secret = 'CT6AhZDFDkn5I18e072dYTVTVB2Plhpw9EzpPPUB55eHucIT'
            with open(f"images/{image.name}",'rb') as image:
                data = {'data': image}
                keywords = requests.post('https://api.everypixel.com/v1/keywords', files=data, auth=(client_id, client_secret)).json()
            
            print(keywords['keywords'][0]['keyword'])
            spotify_search = client.search(keywords['keywords'][0]['keyword'])
            n = random.randint(0, len(spotify_search['playlists']['items']))
            playlist_link = spotify_search['playlists']['items'][n]['external_urls']['spotify']
            playlist_link = embedify(playlist_link)
            context = {
                'playlist_link': playlist_link
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
