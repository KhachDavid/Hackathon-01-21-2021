from django import forms
from .models import NewImage

class NewImageForm(forms.ModelForm):
    class Meta:
        model = NewImage
        fields = ['image']