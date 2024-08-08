# views.py

from .forms import AlocacaoPuraForm
from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd

CARGOS_FILE_PATH = 'D:/1Desktop/Documentos/My Web Sites/App py/ProjetoCastan/Cargos.xlsx'

df = pd.read_excel(CARGOS_FILE_PATH)

def autocomplete_funcionarios(request):
    if request.method == 'GET':
        term = request.GET.get('term', '')
        df = pd.read_excel(CARGOS_FILE_PATH)
        cargos = df[df['Nome do Cargo'].str.contains(term, na=False, case=False)]['Nome do Cargo'].tolist()
        return JsonResponse(cargos, safe=False)

def obter_salario(request):
    if request.method == 'GET':
        cargo = request.GET.get('cargo', '')
        df = pd.read_excel(CARGOS_FILE_PATH)
        salario = df.loc[df['Nome do Cargo'] == cargo, 'Salário'].values
        if salario.size > 0:
            return JsonResponse({'salario': float(salario[0])}, safe=False)
        return JsonResponse({'salario': None}, safe=False)

def calcular(request):
    if request.method == 'POST':
        form = AlocacaoPuraForm(request.POST)
        if form.is_valid():
            cargo = form.cleaned_data['cargo']
            df = pd.read_excel(CARGOS_FILE_PATH)
            salario = df.loc[df['Nome do Cargo'] == cargo, 'Salário'].values[0]
            form.fields['salario'].initial = salario
    else:
        form = AlocacaoPuraForm()

    return render(request, 'calculos/formulario.html', {'form': form})