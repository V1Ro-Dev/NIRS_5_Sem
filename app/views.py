from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.shortcuts import render, redirect
from app import forms
from app import models


def paginate(object_list, request, per_page=9):
    paginator = Paginator(object_list, per_page)
    page = request.GET.get('page', 1)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')

    try:
        current_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        raise Http404("Page not found")

    return current_page, query_params.urlencode()


def index(request):
    return render(request, 'index.html')


def login(request):
    if request.method == "POST":
        login_form = forms.LoginForm(request.POST)
        if login_form.is_valid():
            user = auth.authenticate(request, **login_form.cleaned_data)
            if user is not None:
                auth.login(request, user)
                return redirect('index')
            else:
                login_form.add_error(None, "Wrong username or password!")
    else:
        login_form = forms.LoginForm()

    return render(request, 'login.html',{'form': login_form})


def logout(request):
    auth.logout(request)
    return redirect('index')


def signup(request):
    return render(request, 'signup.html')


def settings(request):
    return render(request, 'settings.html')


def rooms_and_bookings(request):
    return render(request, 'rooms.html')


def rooms(request, room_type):
    if request.method == 'GET':
        check_rooms_form = forms.CheckAvailabilityForm(request.GET)
        if check_rooms_form.is_valid():
            availability, query_params = paginate(
                models.Rooms.objects.get_available_rooms(**check_rooms_form.cleaned_data),
                request
            )
            return render(request, 'room.html', {
                'rooms': availability,
                'query_params': query_params,
                'check_in': request.GET.get('check_in'),
                'check_out': request.GET.get('check_out'),
            })
    else:
        check_rooms_form = forms.CheckAvailabilityForm()
    return render(request, 'room.html', {'check_rooms_form': check_rooms_form})


def booking(request):
    if request.method == 'GET':
        check_rooms_form = forms.CheckAvailabilityForm(request.GET)
        if check_rooms_form.is_valid():
            availability, query_params = paginate(
                models.Rooms.objects.get_available_rooms(**check_rooms_form.cleaned_data),
                request
            )
            return render(request, 'booking.html', {
                'rooms': availability,
                'query_params': query_params,
                'check_in': request.GET.get('check_in'),
                'check_out': request.GET.get('check_out'),
                'check_rooms_form': check_rooms_form
            })
    else:
        check_rooms_form = forms.CheckAvailabilityForm()
    return render(request, 'booking.html', {'check_rooms_form': check_rooms_form})


@login_required()
def book_room(request, room_id):
    return render(request, 'room-booking.html', context={'room_id': room_id})


def contacts(request):
    return render(request, 'contacts.html')
