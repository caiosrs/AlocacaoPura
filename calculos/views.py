from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .forms import AlocacaoPuraForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

CARGOS_FILE_PATH = 'D:/1Desktop/Documentos/My Web Sites/App py/ProjetoCastan/Cargos.xlsx'

def formatar_para_float(valor):
    """ Substitui a vírgula por ponto e converte para float. """
    return float(valor.replace('.', '').replace(',', '.'))

def formatar_numero(valor):
    """ Formata o número para usar vírgula como separador decimal e ponto como separador de milhar. """
    return "{:,.2f}".format(valor).replace('.', ',').replace(',', '.', 1)

@csrf_exempt
def salvar_pdf_resumido(request):
    if request.method == 'POST':
        try:
            # Recebe o valor do cargo e monta o título do PDF
            cargo = request.POST.get('cargo', 'Desconhecido')
            titulo_pdf = f'Memorial de Cálculo | {cargo}'
            
            # Formata os valores recebidos
            salario = formatar_para_float(request.POST.get('salario', '0'))
            encargos_sociais = formatar_para_float(request.POST.get('encargos_sociais', '0'))
            total_beneficios = formatar_para_float(request.POST.get('total_beneficios', '0'))
            total_servico_prestado = formatar_para_float(request.POST.get('total_servico_prestado', '0'))
            despesas_operacionais = formatar_para_float(request.POST.get('despesas_operacionais', '0'))
            lucro = formatar_para_float(request.POST.get('lucro', '0'))
            preco_venda_sem_impostos = formatar_para_float(request.POST.get('preco_venda_sem_impostos', '0'))
            preco_venda_com_impostos = formatar_para_float(request.POST.get('preco_venda_com_impostos', '0'))

            # Formata os valores para exibição
            salario = formatar_numero(salario)
            encargos_sociais = formatar_numero(encargos_sociais)
            total_beneficios = formatar_numero(total_beneficios)
            total_servico_prestado = formatar_numero(total_servico_prestado)
            despesas_operacionais = formatar_numero(despesas_operacionais)
            lucro = formatar_numero(lucro)
            preco_venda_sem_impostos = formatar_numero(preco_venda_sem_impostos)
            preco_venda_com_impostos = formatar_numero(preco_venda_com_impostos)

            agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            # Adicionar imagem ao PDF
            imagem_path = r'D:\1Desktop\Documentos\My Web Sites\App py\ProjetoCastan\alocacao_pura\calculos\static\img\informatec_servicos_em_rh.jpg'
            p.drawImage(imagem_path, 150, height - 200, width=200, height=100)
            
            # Adicionar título ao PDF
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, height - 240, titulo_pdf)

            # Adicionar data e hora ao PDF
            p.setFont("Helvetica", 12)
            p.drawString(100, height - 255, f"Gerado em: {agora}")
            
            # Adicionar conteúdo ao PDF
            p.setFont("Helvetica", 12)
            y = height - 280
            p.drawString(100, y, f"Salário: R${salario}")
            y -= 20
            p.drawString(100, y, f"Encargos Sociais: R${encargos_sociais}")
            y -= 20
            p.drawString(100, y, f"Total Benefícios: R${total_beneficios}")
            y -= 20
            p.drawString(100, y, f"Total do Serviço Prestado: R${total_servico_prestado}")
            y -= 20
            p.drawString(100, y, f"Despesas Operacionais: R${despesas_operacionais}")
            y -= 20
            p.drawString(100, y, f"Lucro: R${lucro}")
            y -= 20
            p.drawString(100, y, f"Preço de Venda sem Impostos: R${preco_venda_sem_impostos}")
            y -= 20
            p.drawString(100, y, f"Preço de Venda com Impostos: R${preco_venda_com_impostos}")

            p.showPage()
            p.save()

            buffer.seek(0)
            return HttpResponse(buffer, content_type='application/pdf')
        except Exception as e:
            return HttpResponse(f"Erro ao gerar o PDF: {str(e)}", status=500)
    else:
        return HttpResponse("Método não permitido", status=405)
    
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