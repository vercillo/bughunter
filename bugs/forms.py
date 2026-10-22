
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Bug, Comment


class BugForm(forms.ModelForm):
    """Regular users can create bugs and edit their own report details."""

    class Meta:
        model = Bug
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "e.g. Withdrawal button does not work",
            }),
            "description": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Describe the steps to reproduce the bug...",
            }),
        }


class TechBugEditForm(forms.ModelForm):
    """Tech Team members can change severity and status only."""

    class Meta:
        model = Bug
        fields = ["severity", "status"]


class SuperuserBugEditForm(forms.ModelForm):
    """Superusers can edit all manually managed bug fields."""

    class Meta:
        model = Bug
        fields = ["title", "description", "severity", "status"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "e.g. Withdrawal button does not work",
            }),
            "description": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Describe the steps to reproduce the bug...",
            }),
        }


class BugAssignmentForm(forms.ModelForm):
    """Bugs can be assigned to superusers or Tech Team members."""

    class Meta:
        model = Bug
        fields = ["assigned_to"]
        labels = {"assigned_to": "Assign to"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["assigned_to"].queryset = (
            User.objects.filter(
                Q(is_superuser=True) | Q(groups__name="Tech Team")
            )
            .distinct()
            .order_by("username")
        )

        self.fields["assigned_to"].required = False
        self.fields["assigned_to"].empty_label = "Unassigned"


class RegistrationForm(UserCreationForm):
    """Public registration creates a regular user account."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user


class TechStaffCreationForm(UserCreationForm):
    """Form for superusers to create Tech Team accounts."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        # These accounts are Tech Team users, not superusers.
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()

        return user


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Write a comment...",
            }),
        }
