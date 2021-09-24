from django.urls import path
import api.views.boardgames as bg

urlpatterns = [
    # Board games
    path('players', bg.PlayersView.as_view(), name='players'),
    path('players/<int:id>', bg.PlayerView.as_view(), name='player'),
    path('board_games', bg.BoardGamesView.as_view(), name='board_games'),
    path('board_games/<int:id>', bg.BoardGameView.as_view(), name='board_game'),
    path('matches', bg.MatchesView.as_view(), name='matches'),
    path('matches/<int:id>', bg.MatchView.as_view(), name='match')

    # Games
]