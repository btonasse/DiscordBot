from django.db import models
from datetime import datetime

class Player(models.Model):
    name = models.CharField(max_length=30, unique=True),
    discord_id = models.IntegerField(unique=True)

    def __str__(self):
        return self.name

class BoardGame(models.Model):
    name = models.CharField(max_length=30),
    #author = models.ManyToManyField() todo
    bgg_id = models.IntegerField(unique=True)
    more_points_win = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Result(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    points = models.IntegerField()

    def __str__(self):
        return f"{self.player.name} - {self.points}"

class Match(models.Model):
    game = models.ForeignKey(BoardGame, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    results = models.ManyToManyField(Result)

    def __str__(self):
        return f"{self.game.name} {self.game.id} - {datetime.strftime(self.date, '%Y-%m-%d')}"


