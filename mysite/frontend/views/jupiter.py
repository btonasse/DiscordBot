from django.shortcuts import render
import requests

BASE_URL = 'http://127.0.0.1:8000'

def index(request):
    pagenum = request.GET.get('page', 1)
    resp = requests.get(f"{BASE_URL}/api/jupiter/characters?page={pagenum}")
    data = resp.json()
    context = {
        'characters': data.pop('results'),
        'pagination': data
    }
    
    return render(request, 'frontend/jupiter/index.html', context)