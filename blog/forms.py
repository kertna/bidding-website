from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from blog.models import Post
from django.forms import HiddenInput
from .models import Profile
class UserRegisterForm(UserCreationForm):
	email=forms.EmailField()

	class Meta:
		model=User
		fields=['username','email','password1','password2']

class UserUpdateForm(forms.ModelForm):
	email=forms.EmailField()

	class Meta:
		model=User
		fields=['username','email']

class ProfileUpdateForm(forms.ModelForm):
	class Meta:
		model=Profile
		fields=['image']

class SellForm(forms.ModelForm):
	
	class Meta:
		model=Post
		fields=['title','minprice','image','category','description','endtime']
		


	def __init__(self, *args, **kwargs):
		self._user = kwargs.pop('author')
		super(SellForm, self).__init__(*args,**kwargs)
		

	def save(self, commit=True):
		inst = super(SellForm, self).save(commit=False)
		inst.author = self._user
		if commit:
			inst.save()
			self.save_m2m()
		return inst

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100,required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(required=True,widget=forms.Textarea)

class AddressForm(forms.Form):
	name = forms.CharField(max_length=100,required=True)
	street=forms.CharField(max_length=100,required=True)
	city = forms.CharField(max_length=100,required=True)
	state = forms.CharField(max_length=100,required=True)
	pincode = forms.CharField(max_length=10,required=True)
	country = forms.CharField(max_length=100,required=True)
	phone = forms.CharField(max_length=10,required=True)
		