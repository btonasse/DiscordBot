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
class EquipmentPerkSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(queryset=md.Perk.objects.all(), slug_field='name', source='perk')
    class Meta:
        model = md.EquipmentPerk
        exclude = ['id', 'character_equipment', 'perk']
class CharacterLocationSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(queryset=md.Location.objects.all(), slug_field='name', source='location')
    event = serializers.SlugRelatedField(queryset=md.Event.objects.all(), slug_field='name', allow_null=True)
    class Meta:
        model = md.CharacterLocation
        exclude = ['id', 'location', 'character']
class CharacterTraitSerializer(serializers.ModelSerializer):
    short_name = serializers.SlugRelatedField(queryset=md.Trait.objects.all(), slug_field='short_name', source='trait')
    class Meta:
        model = md.CharacterTrait
        exclude = ['id', 'trait', 'character']
class CharacterKillSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(queryset=md.Monster.objects.all(), slug_field='name', source='monster')
    class Meta:
        model = md.CharacterKill
        exclude = ['id', 'monster', 'character']
class CharacterInventorySerializer(serializers.ModelSerializer):
    item = serializers.SlugRelatedField(queryset=md.Item.objects.all(), slug_field='name')
    class Meta:
        model = md.CharacterInventory
        exclude = ['id', 'character']
class CharacterEquipmentSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(queryset=md.Equipment.objects.all(), slug_field='name', source='equipment')
    perks = EquipmentPerkSerializer(source='equipmentperk_set', many=True)
    class Meta:
        model = md.CharacterEquipment
        fields = ['name', 'slot', 'rarity', 'mod_code', 'perks']
class PerksRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        name = value.perk.name
        if value.level:
            name += f" {value.level}"
        return name
    def to_internal_value(self, data):
        try:
            perk = md.Perk.objects.get(name=data['name'])
        except KeyError:
            raise serializers.ValidationError(f"No name specified for perk: {data}")
        except md.Perk.DoesNotExist:
            raise serializers.ValidationError(f"The perk {data} does not exist yet.")
        return perk
class TraitsRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return f"{value.order}: {value.trait.name} {value.level}"
    def to_internal_value(self, data):
        try:
            trait = md.Trait.objects.get(short_name=data)
        except md.Trait.DoesNotExist:
            raise serializers.ValidationError(f"The trat {data} does not exist yet.")
        return trait
class KillsRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return f"{value.monster.name}: {value.howmany}"
    def to_internal_value(self, data):
        try:
            monster_name = md.Monster.objects.get(name=data)
        except md.Monster.DoesNotExist:
            raise serializers.ValidationError(f"The monster {data} does not exist yet.")
        return monster_name
class LocationsRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        name = f"{value.order}: {value.location.name}"
        if value.event:
            name += f" - {value.event}"
        return name
    def to_internal_value(self, data):
        try:
            loc_name = md.Location.objects.get(name=data)
        except md.Location.DoesNotExist:
            raise serializers.ValidationError(f"The location {data} does not exist yet.")
        return loc_name
class InventoryRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return f"{value.item.name}: {value.howmany}"
    def to_internal_value(self, data):
        try:
            item = md.Item.objects.get(name=data)
        except md.Item.DoesNotExist:
            raise serializers.ValidationError(f"The item {data} does not exist yet.")
        return item
class PrettyCharacterEquipmentSerializer(serializers.ModelSerializer):
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
        exclude = ['id', 'character', 'equipment']
class PrettyCharacterSerializer(serializers.ModelSerializer): #Pretty version, but might be more useful to get the actual serialized representation of each nested field?
    klass = serializers.StringRelatedField()
    killed_by = serializers.StringRelatedField()
    awards = serializers.StringRelatedField(many=True, required=False)
    traits = TraitsRelatedField(source='charactertrait_set', queryset=md.CharacterTrait.objects.all(), many=True)
    kills = KillsRelatedField(source='characterkill_set', queryset=md.CharacterKill.objects.all(), many=True)
    visited_locations = LocationsRelatedField(source='characterlocation_set', queryset=md.CharacterLocation.objects.all(), many=True)
    inventory = InventoryRelatedField(source='characterinventory_set', queryset=md.CharacterInventory.objects.all(), many=True)
    equipment = CharacterEquipmentSerializer(source='characterequipment_set', many=True)
    
    def create(self, validated_data):
        '''awards = validated_data.pop('awards', [])
        traits = validated_data.pop('traits', [])
        kills = validated_data.pop('kills', [])
        visited_locations = validated_data.pop('visited_locations', [])
        inventory = validated_data.pop('inventory', [])
        equipment = validated_data.pop('equipment', [])'''
        awards = validated_data.pop('awards', [])
        traits = validated_data.pop('charactertrait_set', [])
        kills = validated_data.pop('characterkill_set', [])
        visited_locations = validated_data.pop('characterlocation_set', [])
        inventory = validated_data.pop('characterinventory_set', [])
        equipment = validated_data.pop('characterequipment_set', [])
        
        character = md.Character.objects.create(**validated_data)
        return character
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        model = md.Character
        fields = ['id', 'name', 'level', 'klass', 'won', 'turns_survived', 'killed_by', 'run_time', 'seed', 'points', 'difficulty', 'total_enemies', 'awards', 'visited_locations', 'traits', 'kills', 'equipment', 'inventory']

class CharacterSerializer(serializers.ModelSerializer): 
    klass = serializers.SlugRelatedField(queryset=md.Klass.objects.all(), slug_field='name')
    killed_by = serializers.SlugRelatedField(queryset=md.Monster.objects.all(), slug_field='name')
    awards = AwardSerializer(many=True, required=False)
    traits = CharacterTraitSerializer(source='charactertrait_set', many=True)
    kills = CharacterKillSerializer(source='characterkill_set', many=True)
    visited_locations = CharacterLocationSerializer(source='characterlocation_set', many=True)
    inventory = CharacterInventorySerializer(source='characterinventory_set', many=True)
    equipment = CharacterEquipmentSerializer(source='characterequipment_set', many=True)
    
    def create(self, validated_data):
        '''awards = validated_data.pop('awards', [])
        traits = validated_data.pop('traits', [])
        kills = validated_data.pop('kills', [])
        visited_locations = validated_data.pop('visited_locations', [])
        inventory = validated_data.pop('inventory', [])
        equipment = validated_data.pop('equipment', [])'''
        awards = validated_data.pop('awards', [])
        traits = validated_data.pop('charactertrait_set', [])
        kills = validated_data.pop('characterkill_set', [])
        visited_locations = validated_data.pop('characterlocation_set', [])
        inventory = validated_data.pop('characterinventory_set', [])
        equipment = validated_data.pop('characterequipment_set', [])
        
        character = md.Character.objects.create(**validated_data)
        return character
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        model = md.Character
        fields = ['id', 'name', 'level', 'klass', 'won', 'turns_survived', 'killed_by', 'run_time', 'seed', 'points', 'difficulty', 'total_enemies', 'awards', 'visited_locations', 'traits', 'kills', 'equipment', 'inventory']
