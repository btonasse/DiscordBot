from django.shortcuts import render

BASE_URL = 'http://127.0.0.1:8000'

def index(request):
    return render(request, 'frontend/index.html')