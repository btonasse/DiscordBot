from rest_framework import generics

from django.shortcuts import get_object_or_404

from .models import Player, BoardGame, Match, Result
from .serializers import PlayerSerializer, BoardGameSerializer

class BaseListOrRetrieve(generics.ListCreateAPIView, generics.RetrieveAPIView):
    def get_object(self):
        queryset = self.get_queryset()
        filter = {}
        for field in self.lookup_fields:
            if self.request.data.get(field): 
                filter[field] = self.request.data[field]
        obj = get_object_or_404(queryset, **filter)
        return obj
    
    def get(self, request, *args, **kwargs):
        if not request.data:
            return self.list(request, *args, **kwargs)
        else:
            return self.retrieve(request, *args, **kwargs)

class PlayersView(BaseListOrRetrieve):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    lookup_fields = ['name', 'handle', 'id']

class PlayerView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    lookup_field = 'id'

class BoardGamesView(BaseListOrRetrieve):
    queryset = BoardGame.objects.all()
    serializer_class = BoardGameSerializer
    lookup_fields = ['name', 'bgg_id']

class BoardGameView(generics.RetrieveDestroyAPIView):
    queryset = BoardGame.objects.all()
    serializer_class = BoardGameSerializer
    lookup_field = 'id'

