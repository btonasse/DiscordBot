from django.db import models
from datetime import datetime
from django.utils import timezone

class Player(models.Model):
    handle = models.CharField(max_length=30)
    name = models.CharField(max_length=64)
    discord_id = models.IntegerField(unique=True)

    def __str__(self):
        return self.handle

class BoardGame(models.Model):
    name = models.CharField(max_length=30, unique=True)
    bgg_id = models.IntegerField(unique=True)
    bgg_link = models.URLField(unique=True)
    more_points_win = models.BooleanField(default=True)

    def __str__(self):
        return self.name
        
class Match(models.Model):
    game = models.ForeignKey(BoardGame, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.game.name} {self.game.id} - {datetime.strftime(self.date, '%Y-%m-%d')}"

class Result(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    points = models.IntegerField()
    match = models.ForeignKey(Match, related_name='results', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.player.name} - {self.points}"
