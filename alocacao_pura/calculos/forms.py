from django import forms
import pandas as pd
from .models import CalculoAlocacaoPura
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import locale

# Definindo o caminho do arquivo de cargos
CARGOS_FILE_PATH = 'D:/1Desktop/Documentos/My Web Sites/App py/ProjetoCastan/Cargos.xlsx'

# Configura o locale para o padrão brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def formatar_valor(valor):
    """Formata o valor no padrão brasileiro (milhares com ponto e decimais com vírgula)."""
    return locale.format_string('%.2f', valor, grouping=True)

class AlocacaoPuraForm(forms.ModelForm):
    class Meta:
        model = CalculoAlocacaoPura
        fields = [
            'cargo', 'salario', 'assistencia_medica', 'assistencia_odonto',
            'seguro', 'vr', 'va', 'vt', 'gympass',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar', css_class='btn-primary'))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        # Definindo valores padrão formatados e editáveis
        self.fields['assistencia_medica'].initial = formatar_valor(450.00)
        self.fields['assistencia_odonto'].initial = formatar_valor(21.96)
        self.fields['seguro'].initial = formatar_valor(7.27)
        self.fields['vr'].initial = formatar_valor(605.00)
        self.fields['va'].initial = formatar_valor(0.00)
        self.fields['vt'].initial = formatar_valor(200.00)
        self.fields['gympass'].initial = formatar_valor(14.73)

    def clean(self):
        cleaned_data = super().clean()
        fields_to_format = [
            'assistencia_medica', 'assistencia_odonto',
            'seguro', 'vr', 'va', 'vt', 'gympass',
        ]
        
        for field in fields_to_format:
            value = cleaned_data.get(field)
            if value:
                # Remove os pontos dos milhares e substitui a vírgula por ponto para conversão numérica
                value = value.replace('.', '').replace(',', '.')
                try:
                    cleaned_data[field] = float(value)
                except ValueError:
                    self.add_error(field, "Por favor, insira um valor numérico válido.")
            else:
                cleaned_data[field] = 0.0
                
        return cleaned_data

def get_cargo_choices():
    df = pd.read_excel(CARGOS_FILE_PATH)
    cargos = [(row['Nome do Cargo'], row['Nome do Cargo']) for index, row in df.iterrows()]
    return cargos

class CalculadoraForm(forms.Form):
    cargo = forms.ChoiceField(choices=get_cargo_choices())
    salario = forms.CharField(max_length=20, required=False)

class AlocacaoPuraForm(forms.Form):
    cargo = forms.CharField(
        label='Cargo', 
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Digite o cargo'})
    )
    salario = forms.FloatField(
        label='Salário', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o salário'})
    )
    assistencia_medica = forms.FloatField(
        label='Assistência Médica', 
        initial=formatar_valor(450.00), 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o valor da assistência médica'})
    )
    assistencia_odonto = forms.FloatField(
        label='Assistência Odontológica', 
        initial=formatar_valor(21.96), 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o valor da assistência odontológica'})
    )
    seguro = forms.FloatField(
        label='Seguro', 
        initial=formatar_valor(7.27), 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o valor do seguro'})
    )
    vr = forms.FloatField(
        label='Vale Refeição', 
        initial=formatar_valor(605.00), 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o valor do vale refeição'})
    )
    va = forms.FloatField(
        label='Vale Alimentação', 
        initial=formatar_valor(0.00), 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o valor do vale alimentação'})
    )
    vt = forms.FloatField(
        label='Vale Transporte', 
        initial=formatar_valor(200.00), 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o valor do vale transporte'})
    )
    gympass = forms.FloatField(
        label='Gym Pass', 
        initial=formatar_valor(14.73), 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o valor do gym pass'})
    )
