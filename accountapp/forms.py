from django import forms 
from masterapp.models import Credential, User, UserGroup

class CredentialForm(forms.ModelForm): 

    product = forms.CharField( max_length=30, min_length=3)
    username = forms.CharField( max_length=30, min_length=3)
    password = forms.CharField( max_length=30, min_length=3)

	# specify the name of model to use 
    class Meta:
        model = Credential
        fields = ['product', 'username', 'password']


class UserForm(forms.ModelForm): 
    username = forms.CharField(max_length=30, min_length=3)
    first_name = forms.CharField( max_length=30, min_length=3)
    last_name = forms.CharField( max_length=30, min_length=3)
    # password = forms.CharField( max_length=30, min_length=3)

	# specify the name of model to use 
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password']

class UserEditForm(forms.ModelForm): 
    username = forms.CharField(max_length=30, min_length=3)
    first_name = forms.CharField( max_length=30, min_length=3)
    last_name = forms.CharField( max_length=30, min_length=3)
    raw_password = forms.CharField( max_length=30, min_length=3)

	# specify the name of model to use 
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'raw_password']


class GroupForm(forms.ModelForm):
     
    name = forms.CharField( max_length=30, min_length=3)
    
	# specify the name of model to use 
    class Meta:
        model = UserGroup
        fields = ['name']
