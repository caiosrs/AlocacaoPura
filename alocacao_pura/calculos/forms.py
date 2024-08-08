# forms.py

from django import forms
import pandas as pd
from .models import CalculoAlocacaoPura
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

CARGOS_FILE_PATH = 'D:/1Desktop/Documentos/My Web Sites/App py/ProjetoCastan/Cargos.xlsx'

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

    def clean(self):
        cleaned_data = super().clean()
        fields_to_default = [
            'cargo', 'salario', 'assistencia_medica', 'assistencia_odonto',
            'seguro', 'vr', 'va', 'vt', 'gympass',
        ]
        
        for field in fields_to_default:
            value = cleaned_data.get(field)
            if value:
                value = value.replace(',', '.')
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

