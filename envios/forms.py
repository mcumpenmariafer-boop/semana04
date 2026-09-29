# envios/forms.py
from django import forms

from clientes.models import Cliente
from rutas.models import Ruta

from .models import Encomienda


class EncomiendaForm(forms.ModelForm):
    """Formulario para registrar / editar una encomienda"""

    class Meta:
        model = Encomienda
        fields = [
            'codigo', 'descripcion', 'peso_kg', 'volumen_cm3',
            'remitente', 'destinatario', 'ruta',
            'costo_envio', 'fecha_entrega_est', 'observaciones',
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control',
                                             'placeholder': 'ENC-2026-0001 (automático)'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'peso_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01',
                                                'min': '0.01'}),
            'volumen_cm3': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01',
                                                    'min': '0'}),
            'remitente': forms.Select(attrs={'class': 'form-select'}),
            'destinatario': forms.Select(attrs={'class': 'form-select'}),
            'ruta': forms.Select(attrs={'class': 'form-select'}),
            'costo_envio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01',
                                                    'min': '0'}),
            'fecha_entrega_est': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'
            ),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'codigo': 'Código de encomienda',
            'peso_kg': 'Peso (kg)',
            'volumen_cm3': 'Volumen (cm³)',
            'costo_envio': 'Costo (S/)',
            'fecha_entrega_est': 'Fecha estimada de entrega',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo clientes activos
        self.fields['remitente'].queryset = Cliente.objects.activos()
        self.fields['destinatario'].queryset = Cliente.objects.activos()
        # Mostrar solo rutas activas
        self.fields['ruta'].queryset = Ruta.objects.activas()
        # Validación client-side: los campos obligatorios llevan 'required'
        for field in self.fields.values():
            if field.required:
                field.widget.attrs['required'] = 'required'

    def clean_peso_kg(self):
        peso = self.cleaned_data.get('peso_kg')
        if peso is not None and peso <= 0:
            raise forms.ValidationError('El peso debe ser mayor que 0.')
        return peso

    def clean(self):
        """Validaciones adicionales a nivel de formulario"""
        cleaned = super().clean()
        remitente = cleaned.get('remitente')
        destinatario = cleaned.get('destinatario')
        if remitente and destinatario and remitente == destinatario:
            raise forms.ValidationError(
                'El remitente y el destinatario no pueden ser la misma persona.'
            )
        return cleaned