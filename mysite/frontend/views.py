from django.shortcuts import render
import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

def index(request):
    resp = requests.get(f"{BASE_URL}/api/jupiter/characters", params={'limit': 1000})
    context = {'characters': resp.json()}
    return render(request, 'frontend/index.html', context)