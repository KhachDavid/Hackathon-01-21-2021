import base64
import datetime
from urllib.parse import urlencode, quote
import requests, json
from .models import Song
from .quick_sort import quick_sort
from .merge_sort import merge_sort
import random
from .Track import Track
from .Song import Song_by
from random import shuffle
import numpy as np
from scipy import stats

def embedify(random_track):
    """
    This function is used to add an embed parameter to the spotify song link
    """
    random_track2 = random_track
    x = random_track2.split("/")
    random_track1 = x[0] + "//" + x[2] + "/embed/" + x[3] + "/" + x[4]  
    # Adding the embed parameter to send through
    # jinja
    return random_track1

class SpotifyAPI(object):
    # This variable gives access to the API
    access_token = None

    access_token_expires = datetime.datetime.now()
    client_id = None
    client_secret = None
    access_token_did_expire = True

    token_url = 'https://accounts.spotify.com/api/token'
    SPOTIFY_API_BASE_URL = "https://api.spotify.com"
    API_VERSION = "v1"
    SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

    scope = "streaming user-follow-read user-read-private playlist-modify-public playlist-modify-private user-top-read user-follow-modify"
    state = ""
    show_dialog_bool = True
    show_dialog_str = str(show_dialog_bool).lower()

    def __init__(self, client_id, client_secret, show_dialog_bool=True,
                 show_no_spotify_dialog_bool=True, *args, **kwargs):
        """
        Constructor Method for the API
        Creates an object using developer account details
        https://developer.spotify.com/dashboard/applications/fb1324d95b384e17a6e4838f3ab7cfb8
        :param client_id: found in the link above
        :param client_secret: found in the link above
        :param args:
        :param kwargs:
        """

        # This just help if we want to inherit from other class
        super().__init__(*args, **kwargs)

        # Initialize values
        self.client_id = client_id
        self.client_secret = client_secret
        self.show_dialog_bool = show_dialog_bool
        self.show_no_spotify_dialog_bool = show_no_spotify_dialog_bool
        SPOTIFY_API_BASE_URL = "https://api.spotify.com"
        API_VERSION = "v1"
        self.SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
        self.tracks = []
        self.counter = 0

    def get_client_credentials(self):
        """
        :return: a base 64 encoded string
        """

        if self.client_secret is None or self.client_id is None:
            raise Exception("You must set client_id or client_secret")

        # client credits must be a base 64 encoded string
        # as per by the documentation of Spotify API
        client_creds = f"{self.client_id}:{self.client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())

        return client_creds_b64.decode()

    def get_token_header(self):
        """
        :return: the token header
        """
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }

    def get_token_data(self):
        """
        Specified by the Spotify API documentation
        :return: the token data
        """
        return {
            "grant_type": "client_credentials"
        }

    def get_token_url(self):
        return self.token_url

    def perform_auth(self):
        """
        This function extracts the access token
        :return: True if successful, raise Exception if unsuccessful
        """

        # Makes an API request
        # Uses the data and the header as per by the documentation
        r = requests.post(self.token_url, data=self.get_token_data(), headers=self.get_token_header())

        # in case the response is not okay
        if r.status_code not in range(200, 299):
            raise Exception('Failed to Authenticate')

        # Jsonify the token data
        data = r.json()

        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']

        # Set the expiration time
        # The moment token was generated + the time it will take to expire
        expires = now + datetime.timedelta(seconds=expires_in)

        # Reinitialize class variables
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        """
        A recursive function that returns the access token itself
        It also prevents the token from expiring
        Once the token is expired, the function will call perform_auth() to reset the token
        :return: the access token
        """
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()

        if expires < now:
            self.perform_auth()
            return self.get_access_token()

        elif token is None:
            self.perform_auth()
            return self.get_access_token()

        return token

    def get_headers(self):
        """
        :return: the header with the token of type bearer
        """

        access_token = self.get_access_token()
        return {
            "Authorization": f"Bearer {access_token}"
        }

    def base_search(self, query_params):
        """
        Makes the final query
        The syntax of function calls is specified in the Spotify API documentation
        :param query_params: The complete query to execute
        :return: A JSON object containing the search results
        """

        # Extract the access token
        headers = self.get_headers()

        endpoint = 'https://api.spotify.com/v1/search'
        lookup_url = f"{endpoint}?{query_params}"

        # Make the API request
        r = requests.get(lookup_url, headers=headers)

        if r.status_code not in range(200, 299):
            return {}

        # Return the results
        return r.json()

    def search(self, query=None, search_type='playlist'):
        """
        Converts the query to a list and creates another dictionary to
        execute a query using the search type and the query itself
        :param query: By default is a list containing the query
        :param search_type: By default is a playlist
        :return: The a JSON object extracted from a base search using a query
        """
        if query is None:
            raise Exception("Query Is Required")

        if isinstance(query, dict):
            # convert dictionary to a list
            query = " ".join([f"{k}:{v}" for k, v in query.items()])

        query_params = urlencode({"q": query, "type": search_type.lower()})
        return self.base_search(query_params)

    def get_resource(self, lookup_id, resource_type='albums', version='v1'):
        """
        Gets a given resource by id
        :param lookup_id:
        :param resource_type:
        :param version: By default is 'v1' as per by the Spotify documentation
        :return:
        """

        # https://api.spotify.com/v1/albums/189237827
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"

        # contains the access token
        # must be in the API request call
        headers = self.get_headers()

        r = requests.get(endpoint, headers=headers)

        if r.status_code not in range(200, 299):
            return {}

        return r.json()

    def get_album(self, _id):
        """
        :param _id: Is an id of an album
        :return: A JSON object containing the results of searching by id
        """
        return self.get_resource(_id)

    def get_artist(self, _id):
        """
        :param _id:  Is an id of an artist
        :return: A JSON object containing the results of searching by id
        """
        return self.get_resource(_id, resource_type='artists')

    # Refresh Token
    def get_show_dialog(self):
        """
        True - if the user has to give access everything signing in with Spotify
        False - if the user has to give access once
        :return:
        """
        return self.show_dialog_bool

    def set_show_dialog_false(self):
        self.show_dialog_bool = False

    def set_show_dialog_true(self):
        self.show_dialog_bool = True

    def get_auth_query(self):
        auth_query_parameters = {
            "response_type": "code",
            "redirect_uri": "http://127.0.0.1:5000/callback",
            "scope": "streaming user-follow-read user-read-private playlist-modify-public playlist-modify-private user-top-read user-follow-modify",
            "state": "",
            "show_dialog": str(self.get_show_dialog()).lower(),
            "client_id": self.client_id
        }

        return auth_query_parameters

    def get_authentication_url(self):
        return "https://accounts.spotify.com/authorize"

    def generate_auth_url(self):
        """
        This function creates an authentication url, which connects the user's spotify account
        """
        url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in self.get_auth_query().items()])
        auth_url = "{}/?{}".format(self.get_authentication_url(), url_args)
        return auth_url

    def get_users_top_artists(self, auth_header, num_entities):
        """ 
        Return list of new user's top and followed artists 
        @Credit: Mahnoor Shafi - https://github.com/mahnoorshafi/Moodify/blob/master/mood.py
        """

        artists = []

        term = ['long_term', 'medium_term']

        for length in term:
            url = f'{self.SPOTIFY_API_URL}/me/top/artists?time_range={length}&limit={num_entities}'
            top_artists_data = requests.get(url, headers=auth_header)
            top_artists_data = top_artists_data.json()
            # top_artists_data = get_spotify_data(request, auth_header)
            top_artists = top_artists_data['items']
            for top_artist in top_artists:
                if top_artist['id'] not in artists:
                    artists.append(top_artist['id'])

        users_followed_artists = f'{self.SPOTIFY_API_URL}/me/following?type=artist&limit={num_entities}'
        followed_artists_data = requests.get(users_followed_artists, headers=auth_header).json()
        # followed_artists_data = get_spotify_data(users_followed_artists, auth_header)

        followed_artists = followed_artists_data['artists']['items']

        for followed_artist in followed_artists:
            if followed_artist['id'] not in artists:
                artists.append(followed_artist['id'])

        return artists

    def get_related_artists(self, auth_header, top_artists):
        """ 
        Return list of related artists using users number one top artist 
        @Credit: Mahnoor Shafi - https://github.com/mahnoorshafi/Moodify/blob/master/mood.py
        """

        new_artists = []

        for artist_id in top_artists[:1]:
            request = f'{self.SPOTIFY_API_URL}/artists/{artist_id}/related-artists'
            related_artists_data = requests.get(request, headers=auth_header).json()
            # related_artists_data = get_spotify_data(request, auth_header)
            related_artists = related_artists_data['artists']

            for related_artist in related_artists:
                if related_artist['id'] not in new_artists:
                    new_artists.append(related_artist['id'])

        artists = set(top_artists + new_artists)

        return list(artists)

    def get_top_tracks(self, auth_header, artists):
        """ Return list containing 10 track ids per artist.
        Add tracks to Track model as well as to UserTrack model
        to associate them with the user. """

        top_tracks = []

        for artist_id in artists:
            request = f'{self.SPOTIFY_API_URL}/artists/{artist_id}/top-tracks?country=US'
            track_data = requests.get(request, headers=auth_header).json()
            # track_data = get_spotify_data(request, auth_header)
            tracks = track_data['tracks']

            for track in tracks:
                # track_uri = track['uri']
                track_id = track['id']
                # track_name = track['name']

                if track['id'] not in top_tracks:
                    top_tracks.append(track['id'])
            

        return top_tracks
    
    def cluster_ids(self, top_tracks, n = 100):
        """ Return list of track ids clustered in groups of 100 """

        clustered_tracks = []
        for i in range(0, len(top_tracks), n):
            clustered_tracks.append(top_tracks[i:i + n])

        return clustered_tracks

    def select_tracks(self, user_audio_features, mood):
        """ Return set of spotify track uri's to add to playlist based on mood. """

        selected_tracks = []

        for track, feature in user_audio_features.items():
            if mood <= 0.10:
                if (0 <= feature['valence'] <= (mood + 0.05)) and (feature['energy'] <= (mood + 0.1)) and (feature['danceability'] <= (mood + 0.2)):
                    selected_tracks.append(track)
            if mood <= 0.25:
                if ((mood - 0.05) <= feature['valence'] <= (mood + 0.05)) and (feature['energy'] <= (mood + 0.1)) and (feature['danceability'] <= (mood + 0.2)):
                    selected_tracks.append(track)
            if mood <= 0.50:
                if ((mood - 0.05) <= feature['valence'] <= (mood + 0.05)) and (feature['energy'] <= (mood + 0.1)) and (feature['danceability'] <= mood):
                    selected_tracks.append(track)
            if mood <= 0.75:
                if ((mood - 0.05) <= feature['valence'] <= (mood + 0.05)) and (feature['energy'] >= (mood - 0.1)) and (feature['danceability'] >= mood):
                    selected_tracks.append(track)
            if mood <= 0.90:
                if ((mood - 0.05) <= feature['valence'] <= (mood + 0.05)) and (feature['energy'] >= (mood - 0.2)) and (feature['danceability'] >= (mood - 0.3)):
                    selected_tracks.append(track)
            if mood <= 1.00:
                if ((mood - 0.1) <= feature['valence'] <= 1) and (feature['energy'] >= (mood - 0.3)) and (feature['danceability'] >= (mood - 0.4)):
                    selected_tracks.append(track)

        shuffle(selected_tracks)
        playlist_tracks = selected_tracks[:36]
        
        return set(playlist_tracks)

    def add_and_get_user_tracks(self,auth_header, clustered_tracks):
        """ Get three audio features for tracks: danceability, energy, valence.
        Add audio features to Track model and delete those that don't have audio
        features. Return list of tracks associated with user.  """

        track_audio_features = []

        for track_ids in clustered_tracks:
            ids = '%2C'.join(track_ids)
            request = f'{self.SPOTIFY_API_URL}/audio-features?ids={ids}'
            audio_features_data = requests.get(request, headers=auth_header).json()
            # audio_features_data = get_spotify_data(request, auth_header)
            audio_features = audio_features_data['audio_features']
            track_audio_features.append(audio_features)

        lst_of_tracks = []
        for tracks in track_audio_features:
            for track in tracks:
                if track:
                    track_uri = track['uri']
                    track_valence = track['valence']
                    track_danceability = track['danceability']
                    track_energy = track['energy']
                    lst_of_tracks.append(Track(track_uri, track_valence, track_energy, track_danceability))
        return lst_of_tracks

    def standardize_audio_features(self, user_tracks):
        """ Return dictionary of standardized audio features. 
        Dict = Track Uri: {Audio Feature: Cumulative Distribution} """


        user_tracks_valence = list(map(lambda track: track.get_valence(), user_tracks))
        valence_array = np.array(user_tracks_valence)
        valence_zscores = stats.zscore(valence_array)
        valence_zscores = valence_zscores.astype(dtype=float).tolist()
        valence_cdf = stats.norm.cdf(valence_zscores)

        user_tracks_energy = list(map(lambda track: track.get_energy(), user_tracks))
        energy_array = np.array(user_tracks_energy)
        energy_zscores = stats.zscore(energy_array)
        energy_zscores = energy_zscores.astype(dtype=float).tolist()
        energy_cdf = stats.norm.cdf(energy_zscores)

        user_tracks_danceability = list(map(lambda track: track.get_danceability(), user_tracks))
        danceability_array = np.array(user_tracks_danceability)
        danceability_zscores = stats.zscore(danceability_array)
        danceability_zscores = danceability_zscores.astype(dtype=float).tolist()
        danceability_cdf = stats.norm.cdf(danceability_zscores)

        user_audio_features = {}

        for i, user_track in enumerate(user_tracks):
            user_audio_features[user_track.get_uri()] = {'valence': valence_cdf[i], 
                                            'energy': energy_cdf[i], 
                                            'danceability': danceability_cdf[i]}
        
        return user_audio_features


    def create_playlist(self, auth_header, playlist_tracks, playlist_name):
        """ Create playlist and add tracks to playlist. """

        request = f'{self.SPOTIFY_API_URL}/me'
        user_info_data = requests.get(request, headers=auth_header).json()
        user_id = user_info_data['id']

        name = f'{playlist_name}'

        payload = { 
            'name' : name,
            'description': 'Mood generated playlist'
            }
        playlist_request = f'{self.SPOTIFY_API_URL}/users/{user_id}/playlists'
        playlist_data = requests.post(playlist_request, data = json.dumps(payload), headers =auth_header).json()
        playlist_id = playlist_data['id']   

        track_uris = '%2C'.join(playlist_tracks)
        add_tracks = f'{self.SPOTIFY_API_URL}/playlists/{playlist_id}/tracks?uris={track_uris}'
        tracks_added = requests.post(add_tracks, headers=auth_header).json()
        # tracks_added = post_spotify_data(add_tracks, auth_header)

        return playlist_data['external_urls']['spotify']

    def get_audio_features(self, auth_header, track_ids):  # track_ids = list of track ids
        """
        This function returns a JSON object with all the audio features of the given list of track ids.
        """
        GET_AUDIOFEAT_ENDPOINT = "{}/{}".format(self.SPOTIFY_API_URL, 'audio-features/?ids=')  # /<track id>

        url = GET_AUDIOFEAT_ENDPOINT  # generate URL to query track ids
        for i in range(len(track_ids)):
            url = url + track_ids[i] + ','

        r_tt = requests.get(url, headers=auth_header)  # Get JSON of each track's audio features
        return r_tt.json()

    def get_song(self, audio_features, high_or_low, song_element):
        """
        Generic implementation of a method that searches 
        for a song based on an element and whether the element
        is high or low
        """
        if len(self.tracks) == 0:
            self.reset_track_count()
            if (len(audio_features) == 1):
                for i in audio_features['audio_features']:
                    new_song = Song_by(i['id'], i['valence'], i['energy'], i['danceability'])
                    self.tracks.append(new_song)
            else:
                for i in range(len(audio_features)):
                    for j in range(int(len(audio_features[i]['audio_features']))):
                        new_song = Song_by(audio_features[i]['audio_features'][j]['id'],
                                        audio_features[i]['audio_features'][j]['valence'],
                                        audio_features[i]['audio_features'][j]['energy'],
                                        audio_features[i]['audio_features'][j]['danceability'])
                        self.tracks.append(new_song)
            
            if len(self.tracks) < 10000:
                quick_sort(self.tracks, 0, len(self.tracks) - 1, song_element)
            else:
                merge_sort(self.tracks, 0, len(self.tracks) - 1, song_element)
        # If low, return a random track below the 25th percentile
        if high_or_low == 'low':
            return self.tracks[:5]
        
        # If high, return a random track above the 75th percentile
        if high_or_low == 'high':
            if len(self.tracks) / 4 == 0:
                n = random.randint(0, 1)
                return self.tracks[n].embed_by_id()
            n = random.randint(int((len(self.tracks) * 3 / 4) - 1), int(len(self.tracks) - 1))
            while self.tracks[n].get_seen() and self.counter != len(self.tracks):
                n = random.randint(int((len(self.tracks) * 3 / 4) - 1), int(len(self.tracks) - 1))
                self.counter += 1
            class_method = getattr(Song_by, "get_" + song_element)
            print(song_element + " is " + str(class_method(self.tracks[n])))
            song_to_return = self.tracks[n]
            self.tracks[n].set_seen_true()
            print(song_to_return.embed_by_id())
            return song_to_return.embed_by_id()

    def get_low_valence_songs(self, audio_features):
        return self.get_song(audio_features, 'low', 'valence')

    def get_high_valence_songs(self, audio_features):
        return self.get_song(audio_features, 'high', 'valence')

    def get_low_danceability_songs(self, audio_features):
        return self.get_song(audio_features, 'low', 'danceability')

    def get_high_danceability_songs(self, audio_features):
        return self.get_song(audio_features, 'high', 'danceability')

    def get_low_energy_songs(self, audio_features):
        return self.get_song(audio_features, 'low', 'energy')

    def get_high_energy_songs(self, audio_features):
        return self.get_song(audio_features, 'high', 'danceability')

    def empty_the_tracks(self):
        self.tracks.clear()
    
    def reset_track_count(self):
        self.counter = 0