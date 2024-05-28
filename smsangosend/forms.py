from django import forms
from .models import SmsangoSendSMS, UserProfile, PhoneBookContacts
# from smsangonumcredit.models import NumberCredits
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *
User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
			'first_name',
			'last_name',
		]

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
			'location',
			'date_of_birth',
            'profile_image',
            'phone',
		]
        widgets = {
            'date_of_birth':forms.DateInput(attrs={'type':'date',}),
            'profile_image':forms.ClearableFileInput(attrs={'type': 'file',}),
            'phone':forms.NumberInput(attrs={'type': 'number', 'placeholder':'2348100001111', 'min':'2347000000000','max':'2349999999999'}),
        }

class SmsangoSendSMSForm(forms.Form):
	sender			= forms.CharField(required=True)
	recipients		= forms.CharField(required=True)
	messagecontent	= forms.CharField(required=True)

class SignUpForm(UserCreationForm):
    #first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    username = forms.CharField(max_length=30, required=True, help_text='Required. Unique username')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    class Meta:
        model = User
        fields = ('username','email','password1', 'password2')

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')
        match = User.objects.filter(email=email)
        
        if match:
	        raise forms.ValidationError('This email address is already in use.')
        else:
        	return email   
    
class phonenumber(forms.Form):
    phone = forms.CharField(required=True)
    class Meta:
        model = UserProfile
        fields = ('phone')
    def clean_phone(self, phone):
        # Check to see if any users already exist with this email as a username.
        try:
            match = UserProfile.objects.filter(phone=phone)
            if match:
                raise forms.ValidationError('This phone number is already in use.')
        except User.DoesNotExist:
            phone = self.cleaned_data.get('phone')
            return phone
    
class PhoneBookContactsForm(forms.Form):
    name_contacts = forms.CharField(required=True)
    contact_numbers = forms.Textarea()
    class Meta:
        model = PhoneBookContacts
        fields = ('name_contacts','contact_numbers', )

class PhoneBookContactsEditForm(forms.Form):
    name_contacts = forms.CharField(required=True)
    contact_numbers = forms.Textarea()
