from rest_framework import generics
import api.jupiter.models as md
import api.jupiter.serializers as ser

class CharactersView(generics.ListAPIView):
    queryset = md.Character.objects.all()
    serializer_class = ser.CharacterSerializer

class CharacterView(generics.RetrieveAPIView):
    queryset = md.Character.objects.all()
    serializer_class = ser.CharacterSerializer
    lookup_field = 'id'
