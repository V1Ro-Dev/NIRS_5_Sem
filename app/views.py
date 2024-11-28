from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.shortcuts import render
from app import forms
from app import models


def paginate(object_list, request, per_page=9):
    paginator = Paginator(object_list, per_page)
    page = request.GET.get('page', 1)
    try:
        paginator.page(page)
    except PageNotAnInteger:
        raise Http404("Page not found")
    except EmptyPage:
        raise Http404("Page not found")
    else:
        return paginator.page(page)


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
    # if room_type in ('lux', 'econom', 'presidential'):
    return render(request, 'room.html', context={'room_type': room_type})
    # else:
    #     return Http404('page not found')


def booking(request):
    if request.method == 'POST':
        check_rooms_form = forms.CheckAvailabilityForm(request.POST)
        if check_rooms_form.is_valid():
            availability = paginate(models.Rooms.objects.get_available_rooms(**check_rooms_form.cleaned_data), request)
            return render(request,
                          'booking.html',
                          context={'rooms': availability,
                                   'check_in': request.POST['check_in'],
                                   'check_out': request.POST['check_out']
                                   }
                          )
    else:
        check_rooms_form = forms.CheckAvailabilityForm()
    return render(request, 'booking.html')


@login_required
def book_room(request):
    pass


def contacts(request):
    return render(request, 'contacts.html')

