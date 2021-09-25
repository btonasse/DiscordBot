from rest_framework import generics
import api.jupiter.models as md
import api.jupiter.serializers as ser

class CharactersView(generics.ListCreateAPIView):
    queryset = md.Character.objects.all()
    serializer_class = ser.CharacterSerializer

class CharacterView(generics.RetrieveUpdateDestroyAPIView):
    queryset = md.Character.objects.all()
    serializer_class = ser.CharacterSerializer
    lookup_field = 'id'
