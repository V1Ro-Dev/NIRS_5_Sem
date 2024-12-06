from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.forms import ValidationError
from app import models


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


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_check = forms.CharField(widget=forms.PasswordInput, required=True)
    phone = forms.CharField(max_length=12, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_check', 'first_name', 'last_name']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).all().count():
            raise ValidationError('Username is already exists!')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_email(email)
        if User.objects.filter(email=email).all().count():
            raise ValidationError('Email is already exists!')
        return email

    def clean_phone(self):
        new_phone = self.cleaned_data.get('phone')
        if models.Clients.objects.filter(phone=new_phone).exists():
            raise ValidationError('Phone is already exists!')
        return new_phone

    def clean(self):
        password = self.cleaned_data.get('password')
        password_check = self.cleaned_data.get('password_check')

        if password != password_check:
            raise ValidationError('Passwords mismatch!')

    def save(self, commit=True):
        user_data = {
            field: self.cleaned_data[field]
            for field in ['username', 'email', 'first_name', 'last_name', 'password']
        }
        phone = self.cleaned_data['phone']
        user = User.objects.create_user(**user_data)
        models.Clients.objects.create(user=user, phone=phone)
        return user


class SettingsForm(forms.ModelForm):
    phone = forms.CharField(max_length=12, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_username(self, **kwargs):
        user = super().save(**kwargs)
        new_username = self.cleaned_data.get('username')
        if User.objects.filter(username=new_username).exists() and new_username != user.username:
            raise ValidationError('Username is already exists!')
        return new_username

    def clean_email(self, **kwargs):
        user = super().save(**kwargs)
        new_email = self.cleaned_data.get('email')
        validate_email(new_email)
        if User.objects.filter(email=new_email).exists() and new_email != user.email:
            raise ValidationError('Email is already exists!')
        return new_email

    def clean_phone(self, **kwargs):
        user = super().save(**kwargs)
        new_phone = self.cleaned_data.get('phone')
        if models.Clients.objects.filter(phone=new_phone).exists() and new_phone != user.phone:
            raise ValidationError('Email is already exists!')
        return new_phone

    def save(self, **kwargs):
        user = super().save(**kwargs)
        client = models.Clients.objects.get(user=user)
        new_username = self.cleaned_data.get('username')
        new_email = self.cleaned_data.get('email')
        new_first_name = self.cleaned_data.get('first_name')
        new_last_name = self.cleaned_data.get('last_name')
        new_phone = self.cleaned_data.get('phone')
        if new_username != user.username:
            user.username = new_username
        if new_email != user.email:
            user.email = new_email
        if new_first_name != user.first_name:
            user.first_name = new_first_name
        if new_last_name != user.last_name:
            user.last_name = new_last_name
        if new_phone != client.phone:
            client.phone = new_phone
            client.save()
        return user


class BookingForm(forms.Form):
    check_in_date = forms.DateField(required=True)
    check_out_date = forms.DateField(required=True)
    payment_option = forms.ChoiceField(
        choices=[
            ('СБП', 'СПБ'),
            ('Наличные', 'Наличные'),
            ('Карта', 'Карта'),
        ],
        required=True
    )
    room_number = forms.CharField(max_length=12, required=True)
    total_price = forms.IntegerField(required=True)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self):
        client = models.Clients.objects.get(user=self.user)
        room = models.Rooms.objects.get(room_number=self.cleaned_data['room_number'])
        booking = models.Bookings.objects.create(renter_id=client,
                                                 room_number=room,
                                                 payment_option=self.cleaned_data['payment_option'],
                                                 check_in_date=self.cleaned_data['check_in_date'],
                                                 check_out_date=self.cleaned_data['check_out_date'])
        booking.save()
        payment = models.Payments.objects.create(
            booking_id=booking,
            amount_paid=self.cleaned_data['total_price'],
            payment_date=self.cleaned_data['check_in_date'],
            payment_method=self.cleaned_data['payment_option']

        )
        payment.save()
        return booking


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = models.Ratings
        fields = ['rating_value', 'rating_feedback']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        if not self.user.is_authenticated:
            raise ValidationError('Войдите/создайте аккаунт, прежде чем писать отзыв')
        client = models.Clients.objects.get(user=self.user)
        if not models.Bookings.objects.filter(renter_id=client).exists():
            raise ValidationError('Вы не можете написать отзыв, т.к еще не бронировали номер')
        return self.cleaned_data

    def save(self):
        client = models.Clients.objects.get(user=self.user)
        booking = models.Bookings.objects.get(renter_id=client)
        rating = models.Ratings.objects.create(booking_id=booking,
                                               rating_value=self.cleaned_data['rating_value'],
                                               rating_feedback=self.cleaned_data['rating_feedback'])
        return rating
