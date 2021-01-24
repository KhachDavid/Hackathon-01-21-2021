class Track(object):
    def __init__(self, uri, valence=0, energy=0, danceability=0):
        """
        :param uri:
        :param valence:
        :param energy:
        :param danceability:
        """
        # This just help if we want to inherit from other class

        self.uri = uri
        self.valence = valence
        self.energy = energy
        self.danceability = danceability

    def get_valence(self):
        return self.valence

    def get_energy(self):
        return self.energy

    def get_danceability(self):
        return self.danceability

    def get_uri(self):
        return self.uri
