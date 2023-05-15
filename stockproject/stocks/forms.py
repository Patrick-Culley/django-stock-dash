from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
from django import forms 
from django.forms import ModelForm
from .models import Users

# CREATE USER REGISTRATION FORM 
class RegisterUserForm(ModelForm): 

    first_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'myfieldclass', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'myfieldclass', 'placeholder': 'Last Name'}))
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class': 'myfieldclass', 'placeholder': 'Email'}))
    username = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'myfieldclass', 'placeholder': 'Username'}))
    password = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'myfieldclass', 'placeholder': 'Password'}))

    class Meta: 
        model = Users
        fields = '__all__'

# CREATE USER LOGIN FORM 
class LoginUserForm(forms.Form): 
    username = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'myfieldclass', 'placeholder': 'Username'}))
    password = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'myfieldclass', 'placeholder': 'Password'}))

