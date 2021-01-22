from django.shortcuts import render

def home(request):
    return render(request, 'main/home.html')
def login(request):
    return render(request, 'main/login.html')