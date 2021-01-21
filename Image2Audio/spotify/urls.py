from django.urls import path
from . import views

urlpatterns = [
    path('', views.auth, name='spotify-auth'),
    path('callback/', views.callback, name='spotify-callback')
]