from django.db import models
from django.utils import timezone


class Song(models.Model):
    id = models.AutoField(primary_key=True)
    song = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    url = models.URLField(max_length=300)
    valence = models.DecimalField(max_digits=7, decimal_places=4)
    energy = models.DecimalField(max_digits=7, decimal_places=4)
    danceability = models.DecimalField(max_digits=7, decimal_places=4)
    # Random Comment

    def __str__(self):
        return self.song

    def get_valence(self):
        return self.valence

    def compare_to(self, other_song):
        return self.valence - other_song.get_valence()

