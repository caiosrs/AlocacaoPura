from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .forms import AlocacaoPuraForm

CARGOS_FILE_PATH = 'D:/1Desktop/Documentos/My Web Sites/App py/ProjetoCastan/Cargos.xlsx'

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

def formatar_numero(valor):
    """ Formata o número para usar vírgula como separador decimal e ponto como separador de milhar. """
    return "{:,.2f}".format(valor).replace('.', ',').replace(',', '.', 1)

@csrf_exempt
def calcular(request):
    if request.method == 'POST':
        form = AlocacaoPuraForm(request.POST)
        if form.is_valid():
            cargo = form.cleaned_data['cargo']
            df = pd.read_excel(CARGOS_FILE_PATH)
            salario = df.loc[df['Nome do Cargo'] == cargo, 'Salário'].values[0]

            assistencia_medica = form.cleaned_data["assistencia_medica"]
            assistencia_odonto = form.cleaned_data["assistencia_odonto"]
            seguro = form.cleaned_data["seguro"]
            vr = form.cleaned_data["vr"]
            va = form.cleaned_data["va"]
            vt = form.cleaned_data["vt"]
            gympass = form.cleaned_data["gympass"]

            encargos_sociais = salario * 0.65
            total_sal_encargos = salario + encargos_sociais

            total_beneficios = assistencia_medica + assistencia_odonto + seguro + vr + va + vt + gympass
            total_servico_prestado = total_sal_encargos + total_beneficios

            despesas_operacionais = total_servico_prestado * 0.05
            lucro = total_servico_prestado * 0.15

            preco_venda_sem_impostos = total_servico_prestado + despesas_operacionais + lucro

            total_impostos = 0.20
            preco_venda_com_impostos = preco_venda_sem_impostos / (1 - total_impostos)

            iss = 0.05
            pis = 0.01
            cofins = 0.03
            ir = 0.08
            csll = 0.03

            iss_calculado = iss * preco_venda_com_impostos
            pis_calculado = pis * preco_venda_com_impostos
            cofins_calculado = cofins * preco_venda_com_impostos
            ir_calculado = ir * preco_venda_com_impostos
            csll_calculado = csll * preco_venda_com_impostos

            context = {
                'Salário': formatar_numero(salario),
                'Assistência Médica': formatar_numero(assistencia_medica),
                'Assistência Odontológica': formatar_numero(assistencia_odonto),
                'Vale Refeição': formatar_numero(vr),
                'Vale Alimentação': formatar_numero(va),
                'Vale Transporte': formatar_numero(vt),
                'Seguro': formatar_numero(seguro),
                'Gym Pass': formatar_numero(gympass),
                'Encargos Sociais (Legais + Provisões)': formatar_numero(encargos_sociais),
                'Total Salário + Encargos': formatar_numero(total_sal_encargos),
                'Total Benefícios': formatar_numero(total_beneficios),
                'Total do Custo do Serviço Prestado': formatar_numero(total_servico_prestado),
                'Despesas Operacionais 5%': formatar_numero(despesas_operacionais),
                'Lucro 15%': formatar_numero(lucro),
                'Preço de Venda sem Impostos': formatar_numero(preco_venda_sem_impostos),
                'ISS': formatar_numero(iss_calculado),
                'PIS': formatar_numero(pis_calculado),
                'Cofins': formatar_numero(cofins_calculado),
                'IR': formatar_numero(ir_calculado),
                'CSLL': formatar_numero(csll_calculado),
                'Total': formatar_numero(iss_calculado + pis_calculado + cofins_calculado + ir_calculado + csll_calculado),
                'Preço de Venda com Impostos - Mês': formatar_numero(preco_venda_com_impostos)
            }
            return JsonResponse(context)
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)
    else:
        form = AlocacaoPuraForm()
        return render(request, 'calculos/formulario.html', {'form': form})