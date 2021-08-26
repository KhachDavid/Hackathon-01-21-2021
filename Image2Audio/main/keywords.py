# Prannav Arora, Ryan Almizyed
# BadgerHacks 2021

import requests
import os
from colorthief import ColorThief
import base64
import Algorithmia
# .env API key storage

client_id = 'J93dlmnXh0XusKixhnpz4K3z'
client_secret = 'CT6AhZDFDkn5I18e072dYTVTVB2Plhpw9EzpPPUB55eHucIT'
ALGORITHMIA_CLIENT_KEY = "KEY"


def get_keywords_from_image(image_name):
    '''
    Returns a list of keywords for a given image
    image_name - the path of the image that is stored within the project folder
    num_keywords - the number of keywords requested

    Original Source - https://labs.everypixel.com/api/docs
    '''

    with open(image_name,'rb') as image:
        data = {'data': image}
        info = requests.post('https://api.everypixel.com/v1/keywords', files=data, auth=(client_id, client_secret)).json()

    keywords = []
    # print(info)
    words = info['keywords']
    for word in words:
        keyword = word['keyword']
        keywords.append(keyword)
    return keywords

