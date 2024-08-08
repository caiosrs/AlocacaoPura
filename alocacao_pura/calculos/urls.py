#calculos/urls.py

from django.urls import path
from . import views
from .views import obter_salario

urlpatterns = [
    path('', views.calcular, name='calcular'),
    path('autocomplete_funcionarios/', views.autocomplete_funcionarios, name='autocomplete_funcionarios'),
    path('obter_salario/', obter_salario, name='obter_salario'),
]
