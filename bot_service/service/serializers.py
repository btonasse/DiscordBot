from rest_framework import serializers
from bot_service.service.models import Player, BoardGame, Result, Match

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class BoardGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardGame
        fields = '__all__'

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

                

                

        

                