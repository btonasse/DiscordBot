from django.urls import path
from api.jupiter import views

urlpatterns = [
    path('characters', views.CharactersView.as_view(), name='characters'),
    path('characters/<int:id>', views.CharacterView.as_view(), name='character')
]