from django import forms
from django.db.models import query_utils

from .base import BaseForm
from catalogo.models import User


class UsuarioForm(BaseForm):
    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','password','confirm_password','administrador','capturista','usuario')

    username = forms.CharField(label='Usuario', widget=forms.TextInput())
    first_name = forms.CharField(label='Nombre(s)', widget=forms.TextInput())
    last_name = forms.CharField(label='Apellidos', widget=forms.TextInput())
    email = forms.CharField(label='Correo electrónico', widget=forms.EmailInput())
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='Cofirmar contraseña', widget=forms.PasswordInput())


    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)


    def clean(self):
        cleaned_data = super(UsuarioForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Las contraseñas no coinciden, inténtelo nuevamente.')


class UsuarioUpdateForm(BaseForm):
    username = forms.CharField(label='Usuario', widget=forms.TextInput())
    first_name = forms.CharField(label='Nombre(s)', widget=forms.TextInput())
    last_name = forms.CharField(label='Apellidos', widget=forms.TextInput())
    email = forms.CharField(label='Correo electrónico', widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'administrador', 'capturista', 'usuario',)

    # Este __init__ debe estar al mismo nivel que class Meta, no dentro
    def __init__(self, *args, **kwargs):
        super(UsuarioUpdateForm, self).__init__(*args, **kwargs)