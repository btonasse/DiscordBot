from django.db import models

class Monster(models.Model):
    name = models.CharField(max_length=64, unique=True)
    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=64, unique=True)
    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=64, unique=True)
    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=64, unique=True)
    def __str__(self):
        return self.name

class Award(models.Model):
    name = models.CharField(max_length=64, unique=True)
    typ = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Klass(models.Model):
    class KlassCode(models.TextChoices):
        MARINE = 'M'
        SCOUT = 'S'
        TECHNICIAN = 'T'
    name = models.CharField(max_length=64, unique=True)
    code = models.CharField(max_length=1, choices=KlassCode.choices)
    def __str__(self):
        return f"{self.name} ({self.code})"

class Trait(models.Model):
    name = models.CharField(max_length=64, unique=True)
    short_name = models.CharField(max_length=3)
    description = models.TextField(blank=True)
    def __str__(self):
        return f"{self.name} ({self.short_name})"

class Perk(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Equipment(models.Model):
    class EquipmentType(models.TextChoices):
        WEAPON = 'W'
        BODY = 'B'
        HEAD = 'H'
        UTILITY = 'U'
        RELIC = 'R'

    name = models.CharField(max_length=64, unique=True)
    typ = models.CharField(max_length=1, choices=EquipmentType.choices)

    def __str__(self):
        return self.name

class Character(models.Model):
    class Difficulty(models.TextChoices):
        EASY = 'E'
        MEDIUM = 'M'
        HARD = 'H'
        ULTRAVIOLENCE = 'U'
        NIGHTMARE = 'N'
    
    name = models.CharField(max_length=64)
    klass = models.ForeignKey(Klass, on_delete=models.CASCADE)
    won = models.BooleanField(default=False)
    level = models.IntegerField(default=1)
    turns_survived = models.IntegerField()
    killed_by = models.ForeignKey(Monster, on_delete=models.CASCADE, blank=True, default=None, null=True)
    run_time = models.DurationField()
    seed = models.IntegerField()
    points = models.IntegerField()
    difficulty = models.CharField(choices=Difficulty.choices, max_length=1)
    total_enemies = models.IntegerField()
    awards = models.ManyToManyField(Award, blank=True)
    traits = models.ManyToManyField(Trait, through='CharacterTrait', blank=True)
    kills = models.ManyToManyField(Monster, through='CharacterKill', related_name='kills', blank=True)
    equipment = models.ManyToManyField(Equipment, through='CharacterEquipment', blank=True)
    inventory = models.ManyToManyField(Item, through='CharacterInventory', blank=True)
    visited_locations = models.ManyToManyField(Location, through='CharacterLocation')

    def __str__(self):
        return f"{self.id}: {self.name} - {self.difficulty}{self.klass.code}"

# 'Through' models ######################################################

class CharacterEquipment(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    slot = models.IntegerField(blank=True, default=None, null=True)
    rarity = models.CharField(max_length=3, blank=True, null=True)
    perks = models.ManyToManyField(Perk, through='EquipmentPerk', blank=True)
    class Meta:
        order_with_respect_to = 'character'
        unique_together = [['character', 'slot']]
    def __str__(self):
        if self.rarity:
            return f"Char {self.character.id}: {self.rarity} {self.equipment.name}"
        return f"Char {self.character.id}: {self.equipment.name}"

class EquipmentPerk(models.Model):
    class PerkSource(models.TextChoices):
        INNATE = 'I'
        POWER = 'P'
        BULK = 'B'
        ACCURACY = 'A'
        CALIBRATION = 'C'
    character_equipment = models.ForeignKey(CharacterEquipment, on_delete=models.CASCADE)
    perk = models.ForeignKey(Perk, on_delete=models.CASCADE)
    source = models.CharField(max_length=1, choices=PerkSource.choices)
    level = models.IntegerField(default=1)
    class Meta:
        order_with_respect_to = 'character_equipment'
        unique_together = [['character_equipment', 'perk']]

class CharacterTrait(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    trait = models.ForeignKey(Trait, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    order = models.IntegerField()
    class Meta:
        order_with_respect_to = 'character'
        unique_together = [['character', 'order'], ['character', 'trait', 'level']]
    def __str__(self):
        return f"Char {self.character.id}: {self.order} - {self.trait.name} {self.level}"

class CharacterKill(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    howmany = models.IntegerField(default=1)
    class Meta:
        order_with_respect_to = 'character'
        unique_together = [['character', 'monster']]
    def __str__(self):
        return f"Char {self.character.id}: {self.monster.name} - {self.howmany}"

class CharacterInventory(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    howmany = models.IntegerField(default=1)
    class Meta:
        order_with_respect_to = 'character'
        unique_together = [['character', 'item']]

class CharacterLocation(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    order = models.IntegerField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, default=None, null=True)
    class Meta:
        order_with_respect_to = 'character'
        unique_together = [['character', 'order'], ['character', 'location']]
    def __str__(self):
        return f"Char {self.character.id}: {self.order} - {self.location.name}"


