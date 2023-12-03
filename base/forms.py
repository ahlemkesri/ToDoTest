from django import forms
from django.contrib.auth import authenticate
from base.models import User, Task


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField()

    def authenticate(self, request, email=None):
        user = authenticate(request, email=email)
        if user is None:
            raise forms.ValidationError("Les informations d'identification ne sont pas valides.")
        return user


class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('email',)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'order', 'parent_task', 'complete']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }