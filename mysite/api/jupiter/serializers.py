from rest_framework import serializers
import api.jupiter.models as md

class MonsterSerializer(serializers.ModelSerializer):
    class Meta:
        model = md.Monster
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = md.Location
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = md.Item
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = md.Event
        fields = '__all__'

class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = md.Award
        fields = '__all__'

class KlassSerializer(serializers.ModelSerializer):
    class Meta:
        model = md.Klass
        fields = '__all__'

class TraitSerializer(serializers.ModelSerializer):
    class Meta:
        model = md.Trait
        fields = ['short_name']

class PerkSerializer(serializers.ModelSerializer):
    class Meta:
        model = md.Perk
        fields = '__all__'

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = md.Equipment
        fields = '__all__'

class CharacterTraitSerializer(serializers.ModelSerializer):
    #name = serializers.ReadOnlyField(source='trait.name')
    class Meta:
        model = md.CharacterTrait
        #exclude = ['id', 'character', 'trait']
        exclude = ['id']


class TraitsRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return f"{value.order}: {value.trait.name} {value.level}"
class KillsRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return f"{value.monster.name}: {value.howmany}"


class CharacterSerializer(serializers.ModelSerializer): #Pretty version, but might be more useful to get the actual serialized representation of each nested field?
    '''
    awards = AwardSerializer(many=True)
    traits = CharacterTraitSerializer(many=True)
    kills = MonsterSerializer(many=True)
    equipment = TraitSerializer(many=True)
    inventory = TraitSerializer(many=True)
    visited_locations = TraitSerializer(many=True)
    '''
    #traits = CharacterTraitSerializer(source='charactertrait_set', many=True)
    #traits = serializers.StringRelatedField(source='charactertrait_set', many=True)
    awards = serializers.StringRelatedField(many=True)
    traits = TraitsRelatedField(source='charactertrait_set', queryset=md.CharacterTrait.objects.all(), many=True)
    kills = KillsRelatedField(source='characterkill_set', queryset=md.CharacterKill.objects.all(), many=True)
    
    def create(self, validated_data):
        return super().create(validated_data)
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        model = md.Character
        fields = '__all__'
