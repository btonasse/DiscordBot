from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Player, BoardGame, Result, Match

import requests
from xml.etree import ElementTree

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

    def get_bgg_link(self, id):
        return f'https://boardgamegeek.com/boardgame/{id}'

    def get_bgg_id(self, name):
        resp = requests.get(f'https://boardgamegeek.com/xmlapi2/search?query={name}&type=boardgame&exact=1')
        if resp.ok:
            try:
                tree = ElementTree.fromstring(resp.content)
                return tree[0].attrib['id']
            except IndexError: #BGG returns a 200 even when game is not found
                raise serializers.ValidationError(f"No game found on BGG with name: {name}")
    
    def create(self, validated_data):
        validated_data['bgg_id'] = self.get_bgg_id(validated_data['name'])
        validated_data['bgg_link'] = self.get_bgg_link(validated_data['bgg_id'])
        bg = BoardGame.objects.create(**validated_data)
        return bg
        

class ResultSerializer(serializers.ModelSerializer):
    player = serializers.SlugRelatedField(queryset=Player.objects.all(), slug_field='name')
    class Meta:
        model = Result
        fields = '__all__'

class MatchSerializer(serializers.ModelSerializer):
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

        instance.game_id = validated_data.get('game', instance.game)
        instance.date    = validated_data.get('date', instance.date)
        instance.save()

        current_results = Result.objects.filter(match=instance)
        new_result_ids  = [result_data.get('id') for result_data in results_data]
        
        for result in current_results:
            if result.id not in new_result_ids:
                instance.results.remove(result)
        
        for new_result_data in results_data:
            new_serializer = ResultSerializer(data=new_result_data)
            if new_serializer.is_valid(raise_exception=True):
                id_to_update = new_result_data.get('id')
                if not id_to_update:
                    new_serializer.create(validated_data=new_result_data)
                else:
                    result_to_update = current_results.get(id=id_to_update)
                    new_serializer.update(result_to_update, validated_data=new_result_data)
        
        return MatchSerializer(instance)

                

                

        

                