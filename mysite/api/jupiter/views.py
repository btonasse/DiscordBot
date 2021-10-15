from rest_framework import generics
import api.jupiter.models as md
import api.jupiter.serializers as ser
from api.jupiter.utils import MortemParser

from django.db.models import Prefetch
class BaseCharacterView(generics.GenericAPIView):
    queryset = md.Character.objects.select_related(
        'killed_by', 'klass', 'challenge').prefetch_related(
            'awards',
            'effects',
            Prefetch('characterlocation_set', queryset=md.CharacterLocation.objects.select_related('location', 'event')),
            Prefetch('charactertrait_set', queryset=md.CharacterTrait.objects.select_related('trait')),
            Prefetch('characterkill_set', queryset=md.CharacterKill.objects.select_related('monster')),
            Prefetch('characterinventory_set', queryset=md.CharacterInventory.objects.select_related('item')),
            Prefetch('characterequipment_set', queryset=md.CharacterEquipment.objects.select_related('equipment').prefetch_related(
                Prefetch('equipmentperk_set', queryset=md.EquipmentPerk.objects.select_related('perk'))
            ))
        )
    def get_serializer_class(self):
        if self.request._request.method == 'GET':
            return ser.CharSerializerReadonly
        return ser.CharacterSerializer
    
class CharactersView(generics.ListCreateAPIView, BaseCharacterView):
    pass

class CharacterView(generics.RetrieveUpdateDestroyAPIView, BaseCharacterView):
    lookup_field = 'id'

class CreateCharFromMortem(generics.CreateAPIView, BaseCharacterView):
    def create(self, request, *args, **kwargs):
        parser = MortemParser()
        data_dict = parser.parse()
        request.data.update(**data_dict)
        return super().create(request, *args, **kwargs)

