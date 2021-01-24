# Hackathon-01-21-2021

If databases don't work, run the following commands:

py manage.py makemigrations
py manage.py migrate

# Overview 

Once authorized, Image2Audio will give you an opportunity to generate a personalized playlists based on a picture that you upload. When the playlist is created you can play it on our page or on your Spotify's playlist library. 

# Tech Stack

Frontend: Javascript, Jinja

Backend: Python, Django

Libraries: text2emotion, scipy, numpy, everypixel

# Setup Installation

You can freely use the Client ID and the Client Secret values. We chose to hardcode them to make it simpler.

On local machine, go to directory where you want to work and clone Image2Audio repository:
```
$ git clone https://github.com/KhachDavid/Hackathon-01-21-2021.git
```

Create a virtual environment in the directory:
```
$ virtualenv env
```

Activate virtual environment:
```
$ source env/bin/activate
```

Install dependencies:
```
$ pip install -r requirements.txt
```

Run the program
```
$ py -m manage.py runserver 5000
```

# Demo
[Link]
⋮
[1]: https://www.youtube.com/watch?v=VjAe_MTgmUs&feature=youtu.be
