#alocacao_pura/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('alocacao-pura/', include('calculos.urls')),
    path('', lambda request: redirect('/alocacao-pura/')),
]