import keywords

IMAGE1 = "https://images.theconversation.com/files/304963/original/file-20191203-66982-1rzdvz4.jpg?ixlib=rb-1.1.0&rect=23%2C15%2C5290%2C3574&q=45&auto=format&w=496&fit=clip"
RYAN_IMAGE = "https://avatars.githubusercontent.com/u/64053382?s=460&u=ca069a45b4faca8c3e5da16867f05d9aa46047d1&v=4"

def main():
    test_get_emotion_from_image("sad_tank.jpg")
    #test_get_emotion_from_url("IMAGE1")
    #test_get_keywords_from_image()
    #test_get_keywords_from_url()


def test_get_keywords_from_image():
    dog_keywords = keywords.get_keywords_from_image('dog.jpg', 5)
    print(dog_keywords)
    print()
    print(keywords.lemmatize(dog_keywords))
    print(keywords.get_dominant_color('dog.jpg'))
    print("Done!")


def test_get_keywords_from_url():
    megamind_keywords = keywords.get_keywords_from_url('https://img-www.tf-cdn.com/movie/2/megamind.jpeg?_v=20150925200307&fit=crop&crop=faces%20entropy&w=1200&h=630', 10)
    print(megamind_keywords)
    print()
    print(keywords.lemmatize(megamind_keywords))
    print(keywords.get_dominant_color('megamind.jpeg'))
    print("Done!")


def test_get_emotion_from_url(image):
    emotions = keywords.get_emotion_from_url(image, 10)
    print("List: " + emotions)
    print("Done!")

def test_get_emotion_from_image(image):
    print("Testing get_emotion_from_image...")
    print(keywords.get_emotion_from_image(image, 5))
    print("Done!")

main()