from django.urls import path
from frontend.views import home, jupiter, taxcalc

urlpatterns = [
    path('', home.index, name='home'),
    path('taxcalc', taxcalc.taxcalc, name='taxcalc'),
    path('jupiter', jupiter.index, name='jupiter')
]

