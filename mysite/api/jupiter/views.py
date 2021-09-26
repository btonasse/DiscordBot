from rest_framework import generics
import api.jupiter.models as md
import api.jupiter.serializers as ser
from api.jupiter.utils import MortemParser

class CharactersView(generics.ListCreateAPIView):
    queryset = md.Character.objects.all()
    serializer_class = ser.CharacterSerializer

class CharacterView(generics.RetrieveUpdateDestroyAPIView):
    queryset = md.Character.objects.all()
    serializer_class = ser.CharacterSerializer
    lookup_field = 'id'

class CreateCharFromMortem(generics.CreateAPIView):
    queryset = md.Character.objects.all()
    serializer_class = ser.CharacterSerializer
    def create(self, request, *args, **kwargs):
        parser = MortemParser()
        data_dict = parser.parse()
        request.data.update(**data_dict)
        return super().create(request, *args, **kwargs)

