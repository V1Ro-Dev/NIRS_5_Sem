from django import forms
from django.contrib.auth.models import User
from django.forms import ValidationError


class CheckAvailabilityForm(forms.Form):
    room_type = forms.CharField()
    check_in = forms.DateField()
    check_out = forms.DateField()


class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(min_length=3, label="Password", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not (User.objects.filter(username=username).all().count()):
            raise ValidationError("Wrong username!")
        return username
