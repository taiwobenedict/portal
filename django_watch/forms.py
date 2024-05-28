from django import forms
from django_watch.models import DjangoWatch

class DjangoWatchForm(forms.ModelForm):
  li_value = forms.CharField(label='Enter Activation Key', widget=forms.TextInput(attrs={'placeholder':''}))
  c = forms.CharField
  class Meta:
      model = DjangoWatch
      fields = ("li_value",)