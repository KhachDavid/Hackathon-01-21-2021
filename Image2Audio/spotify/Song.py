class Song_by(object):
    def __init__(self, track_id='54flyrjcdnQdco7300avMJ', valence=0, energy=0, danceability=0, duration=0, seen=False,
                *args, **kwargs):
        """
        :param valence:
        :param track_href:
        :param args:
        :param kwargs:
        """
        # This just help if we want to inherit from other class
        super().__init__(*args, **kwargs)

        self.valence = valence
        self.track_id = track_id
        self.energy = energy
        self.danceability = danceability
        self.duration = duration
        self.seen = seen

    def get_valence(self):
        return self.valence

    def get_energy(self):
        return self.energy

    def get_danceability(self):
        return self.danceability

    def get_duration(self):
        return int(self.duration) / 1000

    def get_track_id(self):
        return self.track_id

    def compare_to(self, other_song):
        return self.valence - other_song.get_valence()

    def embed_by_id(self):
        return f"https://open.spotify.com/embed/track/{self.track_id}"

    def get_seen(self):
        return self.seen

    def set_seen_true(self):
        self.seen = True

    def set_seen_false(self):
        self.seen = False