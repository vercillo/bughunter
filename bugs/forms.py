from django import forms
from .models import Bug
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class BugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ["title", "description"]

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "e.g. Withdrawal button does not work"
            }),
            "description": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Describe the steps to reproduce the bug.."
            }),
        }


class TechBugEditForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ["title", "description", "severity", "status"]

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "e.g. Withdrawal button does not work"
            }),
            "description": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Describe the steps to reproduce the bug.."
            }),
        }


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user