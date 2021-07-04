from django.urls import path
from . import views

urlpatterns = [
    path('players', views.players, name='players'),
    path('players/<int:id>', views.player, name='player')
]