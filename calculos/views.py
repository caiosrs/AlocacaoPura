from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .forms import AlocacaoPuraForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

CARGOS_FILE_PATH = r'\\10.1.1.2\ti\BaseCalculos\Cargos.xlsx'

def formatar_para_float(valor):
    """ Substitui a vírgula por ponto e converte para float. """
    return float(valor.replace('.', '').replace(',', '.'))

def formatar_numero(valor):
    """ Formata o número para usar vírgula como separador decimal e ponto como separador de milhar. """
    return "{:,.2f}".format(valor).replace(',', 'X').replace('.', ',').replace('X', '.')

def salvar_pdf_completo(request):
    try:
        salario = formatar_para_float(request.POST.get('salario', '0'))
        assistencia_medica = formatar_para_float(request.POST.get('assistencia_medica', '0'))
        assistencia_odonto = formatar_para_float(request.POST.get('assistencia_odonto', '0'))
        seguro = formatar_para_float(request.POST.get('seguro', '0'))
        vale_refeicao = formatar_para_float(request.POST.get('vr', '0'))
        vale_alimentacao = formatar_para_float(request.POST.get('va', '0'))
        vale_transporte = formatar_para_float(request.POST.get('vt', '0'))
        gym_pass = formatar_para_float(request.POST.get('gympass', '0'))

        encargos_sociais = salario * 0.65
        total_sal_encargos = salario + encargos_sociais
        total_beneficios = assistencia_medica + assistencia_odonto + seguro + vale_refeicao + vale_alimentacao + vale_transporte + gym_pass
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

        # Cria o buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Título e data/hora de geração do PDF
        agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        cargo = request.POST.get('cargo', 'Desconhecido')
        titulo_pdf = f'Cálculo de Alocação Pura | {cargo}'

        # Adicionar título e data/hora ao PDF
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Adicionar imagem ao PDF
        imagem_path = r'\\10.1.1.2\TI\BaseCalculos\static\img\informatec_servicos_em_rh.jpg'
        p.drawImage(imagem_path, 125, height - 100, width=125, height=62.5)
            
        # Adicionar título ao PDF
        p.setFont("Helvetica-Bold", 14)
        p.drawString(275, height - 70, titulo_pdf)

        # Adicionar data e hora ao PDF
        p.setFont("Helvetica", 11)
        p.drawString(275, height - 85, f"Gerado em: {agora}")

        # Dados para tabela
        dados = {
            'Salário': formatar_numero(salario),
            'Assistência Médica': formatar_numero(assistencia_medica),
            'Assistência Odontológica': formatar_numero(assistencia_odonto),
            'Seguro': formatar_numero(seguro),
            'Vale Refeição': formatar_numero(vale_refeicao),
            'Vale Alimentação': formatar_numero(vale_alimentacao),
            'Vale Transporte': formatar_numero(vale_transporte),
            'Gym Pass': formatar_numero(gym_pass),
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
            'Total Impostos': formatar_numero(iss_calculado + pis_calculado + cofins_calculado + ir_calculado + csll_calculado),
            'Preço de Venda com Impostos': formatar_numero(preco_venda_com_impostos)
        }

        data = [
            ['Descrição', 'Valor'],
        ]
        for k, v in dados.items():
            data.append([k, v])

        table = Table(data, colWidths=[250, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (-1, -1), (-1, -1), colors.yellow),
            ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
        ]))

        # Adicionar a tabela na posição desejada
        table.wrapOn(p, width, height)
        table.drawOn(p, 125, height - 540)

        # Finalizar o PDF
        p.showPage()
        p.save()

        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Calculo-Alocacao_Pura-{cargo}-{agora}.pdf"'
        return response
    except Exception as e:
        print(f"Erro ao gerar o PDF completo: {e}")
        return HttpResponse(f"Erro ao gerar o PDF: {str(e)}", status=500)

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
            imagem_path = r'\\10.1.1.2\TI\BaseCalculos\static\img\informatec_servicos_em_rh.jpg'
            p.drawImage(imagem_path, 150, height - 100, width=125, height=62.5)
            
            # Adicionar título ao PDF
            p.setFont("Helvetica-Bold", 14)
            p.drawString(300, height - 70, titulo_pdf)

            # Adicionar data e hora ao PDF
            p.setFont("Helvetica", 11)
            p.drawString(300, height - 85, f"Gerado em: {agora}")
            
            # Adicionar conteúdo ao PDF
            p.setFont("Helvetica", 12)
            y = height - 120
            p.drawString(150, y, f"Salário: R${salario}")
            y -= 20
            p.drawString(150, y, f"Encargos Sociais: R${encargos_sociais}")
            y -= 20
            p.drawString(150, y, f"Total Benefícios: R${total_beneficios}")
            y -= 20
            p.drawString(150, y, f"Total do Serviço Prestado: R${total_servico_prestado}")
            y -= 20
            p.drawString(150, y, f"Despesas Operacionais: R${despesas_operacionais}")
            y -= 20
            p.drawString(150, y, f"Lucro: R${lucro}")
            y -= 20
            p.drawString(150, y, f"Preço de Venda sem Impostos: R${preco_venda_sem_impostos}")
            y -= 20
            p.setFont("Helvetica-Bold", 12)
            p.drawString(150, y, f"Preço de Venda com Impostos: R${preco_venda_com_impostos}")

            p.showPage()
            p.save()

            buffer.seek(0)

            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Memorial-Calculo-{cargo}-{agora}.pdf"'
            return response
        except Exception as e:
            print(f"Erro ao gerar o PDF resumido: {e}")
            return HttpResponse(f"Erro ao gerar o PDF: {str(e)}", status=500)
    
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