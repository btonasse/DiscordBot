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
class PerksRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        name = value.perk.name
        if value.level:
            name += f" {value.level}"
        return name

class CharacterEquipmentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    perks = PerksRelatedField(source='equipmentperk_set', queryset=md.EquipmentPerk.objects.all(), many=True)
    def get_full_name(self, instance):
        name = instance.equipment.name
        if instance.rarity:
            name = f"{instance.rarity} {name}"
        if instance.mod_code:
            name += f" {instance.mod_code}"
        return name
    class Meta:
        model = md.CharacterEquipment
        exclude = ['id', 'character', 'mod_code', 'rarity', 'equipment']

class TraitsRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return f"{value.order}: {value.trait.name} {value.level}"
class KillsRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return f"{value.monster.name}: {value.howmany}"
class LocationsRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        name = f"{value.order}: {value.location.name}"
        if value.event:
            name += f" - {value.event}"
        return name
class InventoryRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return f"{value.item.name}: {value.howmany}"

class CharacterSerializer(serializers.ModelSerializer): #Pretty version, but might be more useful to get the actual serialized representation of each nested field?
    #traits = CharacterTraitSerializer(source='charactertrait_set', many=True)
    #traits = serializers.StringRelatedField(source='charactertrait_set', many=True)
    killed_by = serializers.StringRelatedField()
    awards = serializers.StringRelatedField(many=True)
    traits = TraitsRelatedField(source='charactertrait_set', queryset=md.CharacterTrait.objects.all(), many=True)
    kills = KillsRelatedField(source='characterkill_set', queryset=md.CharacterKill.objects.all(), many=True)
    visited_locations = LocationsRelatedField(source='characterlocation_set', queryset=md.CharacterLocation.objects.all(), many=True)
    inventory = InventoryRelatedField(source='characterinventory_set', queryset=md.CharacterInventory.objects.all(), many=True)
    equipment = CharacterEquipmentSerializer(source='characterequipment_set', many=True)
    
    def create(self, validated_data):
        return super().create(validated_data)
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        model = md.Character
        fields = ['id', 'name', 'level', 'won', 'turns_survived', 'killed_by', 'run_time', 'seed', 'points', 'difficulty', 'total_enemies', 'awards', 'visited_locations', 'traits', 'kills', 'equipment', 'inventory']
