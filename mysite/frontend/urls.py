from django.urls import path
from frontend.views import home, jupiter

urlpatterns = [
    path('', home.index, name='home'),    
    path('jupiter', jupiter.index, name='jupiter')
]

