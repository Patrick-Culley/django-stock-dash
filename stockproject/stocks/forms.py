from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
from django import forms 
from django.forms import ModelForm
from .models import Users
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


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
    
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
  

# CREATE USER LOGIN FORM 
class LoginUserForm(forms.Form): 
    username = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'myfieldclass', 'placeholder': 'Username'}))
    password = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'myfieldclass', 'placeholder': 'Password'}))

