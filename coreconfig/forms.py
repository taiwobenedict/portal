from django import forms
from .models import DashboardConfig

class CoreConfigForms(forms.ModelForm):
    
  class Meta:
    model = CoreConfigForms
    fields = (
      "site_name",
      )
