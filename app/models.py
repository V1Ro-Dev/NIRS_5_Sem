import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, ExpressionWrapper, F, Sum
from django.db.models.functions import Coalesce


class BookingManager(models.Manager):
    def check_avaliable(self, check_in, check_out, room, room_type):
        if room in Rooms.objects.get_available_rooms(check_in, check_out, room_type):
            return True
        return False


class RoomManager(models.Manager):
    def get_available_rooms(self, check_in, check_out, room_type):
        days_booked = (check_out - check_in).days + 1
        query = self.filter(
            ~Q(room_number__in=models.Subquery(
                Bookings.objects.filter(
                    Q(check_in_date__lte=check_out) & Q(check_out_date__gte=check_in)
                ).values('room_number')
            ))
        )

        if room_type != "Все типы":
            query = query.filter(type_name=room_type)
        return query.annotate(
            total_price=ExpressionWrapper(
                F('price_per_night') * days_booked,
                output_field=models.IntegerField()
            )
        )

    def top_rooms_by_revenue(self, top_n=3):
        return self.annotate(
            total_revenue=Coalesce(
                Sum('bookings__payments__amount_paid'), 0
            )
        ).order_by('-total_revenue')[:top_n]


class Clients(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default='')
    phone = models.CharField(max_length=12)

    def __str__(self):
        return self.user.username


class Rooms(models.Model):
    ROOM_TYPES = [
        ('Эконом', 'Эконом'),
        ('Люкс', 'Люкс'),
        ('Президентский', 'Президентский'),
    ]
    room_number = models.IntegerField(primary_key=True)
    id = models.UUIDField(default=uuid.uuid4, editable=False)
    type_name = models.TextField(choices=ROOM_TYPES, max_length=32)
    price_per_night = models.IntegerField()
    room_size_sqm = models.IntegerField()

    ROOM_TYPE_PRICES = {
        'Эконом': 3000,
        'Люкс': 7000,
        'Президентский': 15000,
    }

    ROOM_SIZE_SQM = {
        'Эконом': 50,
        'Люкс': 80,
        'Президентский': 100,
    }

    def save(self, *args, **kwargs):
        if self.type_name in self.ROOM_TYPE_PRICES:
            self.price_per_night = self.ROOM_TYPE_PRICES[self.type_name]

        if self.type_name in self.ROOM_SIZE_SQM:
            self.room_size_sqm = self.ROOM_SIZE_SQM[self.type_name]
        super().save(*args, **kwargs)

    objects = RoomManager()

    def __str__(self):
        return f'Номер {self.room_number}'


class Bookings(models.Model):
    PAYMENT_OPTIONS = [
        ('СБП', 'СПБ'),
        ('Наличные', 'Наличные'),
        ('Карта', 'Карта'),
    ]
    renter_id = models.ForeignKey(Clients, on_delete=models.PROTECT)
    room_number = models.ForeignKey(Rooms, on_delete=models.PROTECT, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    payment_option = models.CharField(choices=PAYMENT_OPTIONS, max_length=8)

    def __str__(self):
        return self.renter_id.user.username

    objects = BookingManager()


class Payments(models.Model):
    booking_id = models.ForeignKey(Bookings, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.IntegerField()
    payment_date = models.DateField()
    payment_method = models.CharField()


class Ratings(models.Model):
    booking_id = models.ForeignKey(Bookings, on_delete=models.CASCADE)
    rating_value = models.CharField(null=True, blank=True)
    rating_feedback = models.CharField(max_length=300, null=True, blank=True)
