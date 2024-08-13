#calculos/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('calcular/', views.calcular, name='calculo'),
    path('', views.calcular, name='calcular'),
    path('alocacao-pura/', views.calcular, name='alocacao-pura'),
    path('autocomplete/', views.autocomplete_funcionarios, name='autocomplete_funcionarios'),
    path('obter-salario/', views.obter_salario, name='obter_salario'),
    path('salvar_pdf_resumido/', views.salvar_pdf_resumido, name='salvar_pdf_resumido'),
]