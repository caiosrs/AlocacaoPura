#calculos/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('calcular/', views.calcular, name='calculo'),
    path('', views.calcular, name='calcular'),
    path('alocacao-pura/', views.calcular, name='calcular'),
    path('autocomplete/', views.autocomplete_funcionarios, name='autocomplete_funcionarios'),
    path('obter-salario/', views.obter_salario, name='obter_salario'),
]
