from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Player, BoardGame, Match, Result
from .serializers import PlayerSerializer, BoardGameSerializer

from django.shortcuts import redirect

@api_view(['GET', 'POST'])
def players(request):
    if request.method == 'GET':
        if not request.data:
            all_players = Player.objects.all()
            serializer = PlayerSerializer(all_players, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                params = data_as_dict(request.data)
                player = Player.objects.get(**params)
                return redirect('player', id=player.id)
            except Player.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
    
    else:
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def player(request, id: int):
    try:
        player = Player.objects.get(id=id)
    except Player.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PlayerSerializer(player)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = PlayerSerializer(player, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        player.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def data_as_dict(request_data):
    dic = {}
    for k, v in request_data.items():
        dic[k] = v
    return dic

@api_view(['GET', 'POST'])
def board_games(request):
    if request.method == 'GET':
        if not request.data:
            all_bgs = BoardGame.objects.all()
            serializer = BoardGameSerializer(all_bgs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                params = data_as_dict(request.data)
                bg = BoardGame.objects.get(**params)
                return redirect('board_game', id=bg.id)
            except BoardGame.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
    
    else:
        serializer = BoardGameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
def board_game(request, id: int):
    try:
        bg = BoardGame.objects.get(id=id)
    except BoardGame.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BoardGameSerializer(bg)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    else:
        bg.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)