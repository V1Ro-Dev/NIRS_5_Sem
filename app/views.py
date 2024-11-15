from django.http import Http404
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def login(request):
    return render(request, 'login.html')


def signup(request):
    return render(request, 'signup.html')


def settings(request):
    return render(request, 'settings.html')


def rooms_and_bookings(request):
    return render(request, 'rooms.html')


def rooms(request, room_type):
    if room_type in ('lux', 'econom', 'presidential'):
        return render(request, 'room.html', context={'room_type': room_type})
    else:
        return Http404('page not found')


def booking(request):
    return render(request, 'booking.html')


def contacts(request):
    return render(request, 'contacts.html')

