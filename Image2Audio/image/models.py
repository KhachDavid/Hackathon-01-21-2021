from django.db import models
from PIL import Image

class NewImage(models.Model):
    image = models.ImageField(upload_to='images/')
    
    def __str__(self):
        return self.image.name