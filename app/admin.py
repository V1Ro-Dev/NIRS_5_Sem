from django.contrib import admin

from app import models

admin.site.register(models.Clients)
admin.site.register(models.Bookings)
admin.site.register(models.Rooms)
admin.site.register(models.Payments)
admin.site.register(models.Ratings)
