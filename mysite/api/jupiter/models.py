from django.db import models
from datetime import datetime

class Monster(models.Model):
    name = models.CharField(max_length=64, unique=True)
    class Meta:
        ordering = ['name']    
    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=64, unique=True)
    class Meta:
        ordering = ['name']    
    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=64, unique=True)
    class Meta:
        ordering = ['name']    
    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=64, unique=True)
    class Meta:
        ordering = ['name']    
    def __str__(self):
        return self.name

class Award(models.Model):
    name = models.CharField(max_length=64, unique=True)
    typ = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    class Meta:
        ordering = ['name']    
    def __str__(self):
        return self.name

class Klass(models.Model):
    class KlassCode(models.TextChoices):
        MARINE = 'M'
        SCOUT = 'S'
        TECHNICIAN = 'T'
    name = models.CharField(max_length=64, unique=True)
    code = models.CharField(max_length=1, choices=KlassCode.choices)
    class Meta:
        ordering = ['name']    
    def __str__(self):
        return f"{self.name}"

class Trait(models.Model):
    name = models.CharField(max_length=64, unique=True)
    short_name = models.CharField(max_length=3)
    description = models.TextField(blank=True)
    class Meta:
        ordering = ['name']    
    def __str__(self):
        return f"{self.name} ({self.short_name})"

class Perk(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    class Meta:
        ordering = ['name']
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
    class Meta:
        ordering = ['name']
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
    uploaded_timestamp = models.DateTimeField(default=datetime.now())
    class Meta:
        ordering = ['name']
    def __str__(self):
        return f"{self.id}: {self.name} - {self.difficulty}{self.klass.code}"

# 'Through' models ######################################################

class CharacterEquipment(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    slot = models.IntegerField(blank=True, default=None, null=True)
    rarity = models.CharField(max_length=3, blank=True, null=True) # Might not be the best idea, given that '' is not the same as NULL
    mod_code = models.CharField(max_length=10, blank=True, default=None, null=True) # Idem
    perks = models.ManyToManyField(Perk, through='EquipmentPerk', blank=True)
    class Meta:
        ordering = ['character']
        unique_together = [['character', 'slot']]
    def __str__(self):
        if self.rarity:
            name = f"Char {self.character.id}: {self.rarity} {self.equipment.name}"
        else:
            name = f"Char {self.character.id}: {self.equipment.name}"
        if self.mod_code:
            name += f" {self.mod_code}"
        return name

class EquipmentPerk(models.Model):
    character_equipment = models.ForeignKey(CharacterEquipment, on_delete=models.CASCADE)
    perk = models.ForeignKey(Perk, on_delete=models.CASCADE)
    level = models.IntegerField(blank=True, default=1, null=True)
    class Meta:
        ordering = ['character_equipment']
        unique_together = [['character_equipment', 'perk']]
    def __str__(self):
        if self.level:
            return f"CharEquip {self.character_equipment.id}: {self.perk.name} {self.level}"
        return f"CharEquip {self.character_equipment.id}: {self.perk.name}"

class CharacterTrait(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    trait = models.ForeignKey(Trait, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    order = models.IntegerField()
    class Meta:
        ordering = ['character', 'order']
        unique_together = [['character', 'order'], ['character', 'trait', 'level']]
    def __str__(self):
        return f"Char {self.character.id}: {self.order} - {self.trait.name} {self.level}"

class CharacterKill(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    howmany = models.IntegerField(default=1)
    class Meta:
        ordering = ['character', 'monster']
        unique_together = [['character', 'monster']]
    def __str__(self):
        return f"Char {self.character.id}: {self.monster.name} - {self.howmany}"

class CharacterInventory(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    howmany = models.IntegerField(default=1)
    class Meta:
        ordering = ['character']
        unique_together = [['character', 'item']]
    def __str__(self):
        return f"Char {self.character.id}: {self.item.name} - {self.howmany}"

class CharacterLocation(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    order = models.IntegerField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, default=None, null=True)
    class Meta:
        ordering = ['character', 'order']
        unique_together = [['character', 'order'], ['character', 'location']]
    def __str__(self):
        return f"Char {self.character.id}: {self.order} - {self.location.name}"


