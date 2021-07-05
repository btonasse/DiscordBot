from django.urls import path
from . import views

urlpatterns = [
    path('players', views.PlayersView.as_view(), name='players'),
    path('players/<int:id>', views.PlayerView.as_view(), name='player'),
    path('board_games', views.BoardGamesView.as_view(), name='board_games'),
    path('board_games/<int:id>', views.BoardGameView.as_view(), name='board_game'),
    path('matches', views.MatchesView.as_view(), name='matches'),
    path('matches/<int:id>', views.MatchView.as_view(), name='match')
]