from django import forms

class UploadMiniSeedForm(forms.Form):
    file = forms.FileField(label='Seleccione el archivo MiniSEED')
