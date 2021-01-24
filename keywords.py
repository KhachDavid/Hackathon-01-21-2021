# Prannav Arora, Ryan Almizyed
# BadgerHacks 2021

import requests
import os
import base64
import nltk
from colorthief import ColorThief
from nltk.stem import WordNetLemmatizer
# Emotion analysis
import Algorithmia
# .env API key storage
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

#nltk.download('all') 

EVERYPIXEL_KEY = os.getenv("EVERYPIXEL_KEY")
EVERPIXEL_SECRET = os.getenv("EVERPIXEL_SECRET")
ALGORITHMIA_CLIENT_KEY = os.getenv("ALGORITHMIA_CLIENT_KEY")


def get_keywords_from_url(url, num_keywords):
    '''
    Returns a list of keywords for a given image
    url (string) - the image address of the image
    num_keywords (int) - the number of keywords requested

    Original Source - https://labs.everypixel.com/api/docs
    '''

    params = {'url': url, 'num_keywords': num_keywords}
    info = requests.get('https://api.everypixel.com/v1/keywords', params=params, auth=(EVERYPIXEL_KEY, EVERPIXEL_SECRET)).json()

    keywords = []
    words = info['keywords']
    for word in words:
        keyword = word['keyword']
        keywords.append(keyword)
    return keywords

def get_keywords_from_image(image_name, num_keywords):
    '''
    Returns a list of keywords for a given image
    image_name - the path of the image that is stored within the project folder
    num_keywords - the number of keywords requested

    Original Source - https://labs.everypixel.com/api/docs
    '''

    with open(image_name,'rb') as image:
        data = {'data': image}
        info = requests.post('https://api.everypixel.com/v1/keywords', files=data, auth=(EVERYPIXEL_KEY, EVERPIXEL_SECRET)).json()

    keywords = []
    print(info)
    words = info['keywords']
    for word in words:
        keyword = word['keyword']
        keywords.append(keyword)
    return keywords


def lemmatize(all_keywords):
    '''
    Given a set of keywords, this function lemmatizes each word
    all_keywords (list of strings) - the keywords

    Orignal source - https://www.geeksforgeeks.org/python-lemmatization-with-nltk/
    '''

    lemmatized_words = []
    lemmatizer = WordNetLemmatizer()

    for word in all_keywords:
        temp = lemmatizer.lemmatize(word)
        if temp not in lemmatized_words:
            lemmatized_words.append(temp)

    return lemmatized_words

def get_dominant_color(image):
    '''
    Most prominent color in an image
    image (string) - path of image

    Original Source - Artem Bernatskyi https://stackoverflow.com/questions/3241929/python-find-dominant-most-common-color-in-an-image
    '''

    color_thief = ColorThief(image)
    return color_thief.get_color(quality=1)


def get_emotion_from_url(url, numResults):
    '''
    Determines the 'emotion' of a given image.

    url = url of image
    numResults = number of emotions to return
    
    API: https://algorithmia.com/algorithms/deeplearning/EmotionRecognitionCNNMBP
    '''
    # Algorithmia client
    client = Algorithmia.client(ALGORITHMIA_CLIENT_KEY)

    # Format input
    input = {
        "image": url,
        "numResults": numResults
    }

    # Analyze with Algorithmia's emotion recognition algorithm
    algo = client.algo('deeplearning/EmotionRecognitionCNNMBP/0.1.2')
    algo.set_options(timeout=5) # optional
    result = algo.pipe(input).result
    return result.get("results")

def get_emotion_from_image(image, numResults):
    '''
    Determines the 'emotion' of a given image.

    image = path to a local image
    numResults = number of emotions to return
    '''
    # Encode local image using base64 encoding
    with open(image, "rb") as img_file:
        img_string = base64.b64encode(img_file.read())
    b64_encoded_string = img_string.decode("utf-8")
    # Pass encoded image as url to algorithm
    img_url = "data:image/png;base64," + b64_encoded_string
    return get_emotion_from_url(img_url, numResults)
