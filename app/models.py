from django.db import models
from django.contrib.auth.models import User


class Clients(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default='')
    phone = models.CharField(max_length=12)

    def __str__(self):
        return self.user.username


class Rooms(models.Model):
    ROOM_TYPES = [
        ('econom', 'Эконом'),
        ('lux', 'Люкс'),
        ('presidential', 'Президентский'),
    ]
    room_number = models.IntegerField(primary_key=True)
    type_name = models.TextField(choices=ROOM_TYPES, max_length=32)
    price_per_night = models.IntegerField()
    room_size_sqm = models.IntegerField()
    payment_option = models.TextField(max_length=8)

    def __str__(self):
        return f'Номер {self.room_number}'


class Bookings(models.Model):
    renter_id = models.ForeignKey(Clients, on_delete=models.PROTECT)
    room_number = models.ForeignKey(Rooms, on_delete=models.PROTECT)
    check_in_date = models.DateField()
    check_out_date = models.DateField()

    def __str__(self):
        return self.renter_id.user.username


class Payments(models.Model):
    booking_id = models.ForeignKey(Bookings, on_delete=models.CASCADE)
    amount_paid = models.IntegerField()
    payment_date = models.DateField()
    payment_method = models.CharField()


class Ratings(models.Model):
    booking_id = models.ForeignKey(Bookings, on_delete=models.CASCADE)
    rating_value = models.CharField(null=True, blank=True)
    rating_feedback = models.CharField(max_length=300, null=True, blank=True)
