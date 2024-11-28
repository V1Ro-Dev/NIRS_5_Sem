from django import forms


class CheckAvailabilityForm(forms.Form):
    room_type = forms.CharField()
    check_in = forms.DateField()
    check_out = forms.DateField()
