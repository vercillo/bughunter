from django import forms
from .models import Bug

class BugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ['title', 'description', 'severity', 'status']

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Withdrawal button does not work'
            }),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Describe the steps to reproduce the bug..'
            }),
        }