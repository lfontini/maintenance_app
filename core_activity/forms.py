from django import forms
from .models import Core  # Importe o modelo Core


class BootstrapTextInput(forms.TextInput):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {})['class'] = 'form-control'
        super(BootstrapTextInput, self).__init__(*args, **kwargs)


class BootstrapSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {})['class'] = 'form-control'
        super(BootstrapSelect, self).__init__(*args, **kwargs)


class CoreForm(forms.ModelForm):

    affected_services = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'style': 'height: 90px;'}),
        initial='No services affected'
    )

    class Meta:
        model = Core
        fields = [
            'activity_type',
            'activity_related_to',
            'ign_engineer',
            'internet_id',
            'network_link',
            'pop',
            'status',
            'duration',
            'downtime',
            'start_date',
            'end_date',
            'affected_services',
            'Description',
            'Description_to_customers',
            'location',
            'remote_hands_information',
        ]

        widgets = {
            # Adicionando 'form-control-sm' para reduzir o tamanho
            'activity_type': BootstrapSelect(attrs={'class': 'form-control form-control-lg'}),
            'activity_related_to': BootstrapSelect,
            'ign_engineer': BootstrapSelect,
            'internet_id': BootstrapSelect,
            'network_link': BootstrapSelect,
            'pop': BootstrapSelect,
            'status': BootstrapSelect,
            'duration': BootstrapTextInput(attrs={'readonly': ' true'}),
            'downtime': BootstrapTextInput(attrs={'placeholder': 'example 00:30'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'value': "YYYY-MM-DDTHH:mm:ss"}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'Description': forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 90px;'}),
            'Description_to_customers': forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 90px;'}),
            'location': BootstrapTextInput,
            'remote_hands_information': forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 90px;'}),
        }
