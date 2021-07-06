from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Player, BoardGame, Result, Match

import requests
from xml.etree import ElementTree

from . import utils

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class BoardGameSerializer(serializers.ModelSerializer):
    bgg_id = serializers.IntegerField(read_only=True, required=False)
    bgg_link = serializers.URLField(read_only=True, required=False)
    class Meta:
        model = BoardGame
        fields = '__all__'

    def validate_name(self, value):
        '''
        Converts input to ASCII to avoid duplicate (Bärenpark vs Barenpark) slipping through validation.
        '''
        as_ascii = utils.str_as_ascii(value)
        try:
            if BoardGame.objects.get(name=as_ascii):
                raise ValidationError(f'A BoardGame with name {as_ascii} already exists.')
        except BoardGame.DoesNotExist:
            pass
        return as_ascii

    
    def get_bgg_link(self, id):
        return f'https://boardgamegeek.com/boardgame/{id}'

    def get_bgg_id(self, name):
        resp = requests.get(f'https://boardgamegeek.com/xmlapi2/search?query={name}&type=boardgame')
        if resp.ok:
            tree = ElementTree.fromstring(resp.content)
            for child in tree:
                resp_as_ascii = utils.str_as_ascii(child[0].attrib['value'])
                if resp_as_ascii == name:
                    return child.attrib['id']
            raise serializers.ValidationError(f"No game found on BGG with name: {name}. Found {len(tree)} similar games.")
        else:
            raise serializers.ValidationError(f"Could not connect to BGG.")
            
    def create(self, validated_data):
        validated_data['bgg_id'] = self.get_bgg_id(validated_data['name'])
        validated_data['bgg_link'] = self.get_bgg_link(validated_data['bgg_id'])
        bg = BoardGame.objects.create(**validated_data)
        return bg
        

class ResultSerializer(serializers.ModelSerializer):
    player = serializers.SlugRelatedField(queryset=Player.objects.all(), slug_field='handle')
    #match = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Result
        exclude = ['id', 'match']

class MatchSerializer(serializers.ModelSerializer):
    game = serializers.SlugRelatedField(queryset=BoardGame.objects.all(), slug_field='name')
    results = ResultSerializer(many=True)
    class Meta:
        model = Match
        fields = '__all__'

    def create(self, validated_data):
        results_data = validated_data.pop('results')
        match = Match.objects.create(**validated_data)
        for result_data in results_data:
            Result.objects.create(match=match, **result_data)
        return match

    def update(self, instance, validated_data):
        results_data = validated_data.pop('results', [])
        instance.game = validated_data.get('game', instance.game)
        instance.date    = validated_data.get('date', instance.date)
        instance.save()

        current_results = Result.objects.filter(match=instance)
        new_result_players  = [result_data.get('player') for result_data in results_data]

        for result in current_results:
            print(result.player, new_result_players)
            if result.player not in new_result_players:
                result.delete()
        
        for new_result_data in results_data:
            res_serializer = ResultSerializer(data=new_result_data)
            if res_serializer.is_valid(raise_exception=True):
                player_to_update = new_result_data.get('player')
                try:
                    result_to_update = current_results.get(player=player_to_update)
                    res_serializer.update(result_to_update, validated_data=new_result_data)
                except Result.DoesNotExist:
                    Result.objects.create(match=instance, **new_result_data)
        
        return instance

                

                

        

                