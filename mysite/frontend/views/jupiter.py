from django.shortcuts import render
from django.core.paginator import Paginator
import requests

BASE_URL = 'http://127.0.0.1:8000'

def index(request):
    resp = requests.get(f"{BASE_URL}/api/jupiter/characters")
    data = resp.json()
    p = Paginator(data, 50)
    context = {
        'characters': data,
        'page_obj': p.get_page(request.GET.get('page'))
        }
    
    return render(request, 'frontend/jupiter/index.html', context)