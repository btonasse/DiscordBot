from django.urls import path
from . import views

urlpatterns = [
    path('players', views.players, name='players'),
    path('players/<int:id>', views.player, name='player'),
    path('board_games', views.board_games, name='board_games'),
    path('board_games/<int:id>', views.board_game, name='board_game')
]