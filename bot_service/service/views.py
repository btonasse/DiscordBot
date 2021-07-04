from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Player, BoardGame, Match, Result
from .serializers import PlayerSerializer

@api_view(['GET', 'POST'])
def players(request):
    if request.method == 'GET':
        all_players = Player.objects.all()
        serializer = PlayerSerializer(all_players, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    else:
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
