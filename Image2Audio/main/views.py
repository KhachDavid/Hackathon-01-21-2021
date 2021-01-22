from django.shortcuts import render
from image.forms import NewImageForm
from image.models import NewImage
import requests

def home(request):
    if request.method == 'POST':
        image_form = NewImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            image = image_form.cleaned_data['image']
            image_form.save()
            p = NewImage.objects.get(image=image_form.cleaned_data['image'])

            # https://labs.everypixel.com/api/docs
            client_id = 'J93dlmnXh0XusKixhnpz4K3z'
            client_secret = 'CT6AhZDFDkn5I18e072dYTVTVB2Plhpw9EzpPPUB55eHucIT'
            with open(f'media/{p}','rb') as image:
                data = {'data': image}
                keywords = requests.post('https://api.everypixel.com/v1/keywords', files=data, auth=(client_id, client_secret)).json()
            print(keywords)
            # return redirect('profile')

    else:
        image_form = NewImageForm()
    context = {
        'image_form': image_form
    }

    return render(request, 'main/home.html', context)