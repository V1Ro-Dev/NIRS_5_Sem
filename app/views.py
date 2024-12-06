import datetime
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms import model_to_dict
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from app import forms
from app import models
from django.contrib import messages


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

    return render(request, 'login.html', {'form': login_form})


def logout(request):
    auth.logout(request)
    return redirect('index')


def signup(request):
    if request.method == 'GET':
        user_form = forms.RegisterForm()
    if request.method == 'POST':
        user_form = forms.RegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            if user:
                auth.login(request, user)
                return redirect('index')
            else:
                user_form.add_error(None, 'Error with creating a new account!')
    return render(request, 'signup.html', {'form': user_form})


@login_required(login_url='login')
def settings(request):
    client = get_object_or_404(models.Clients, user=request.user)
    initial_data = model_to_dict(request.user)
    initial_data['phone'] = client.phone

    if request.method == 'GET':
        edit_form = forms.SettingsForm(initial=initial_data)

    elif request.method == 'POST':
        edit_form = forms.SettingsForm(request.POST, instance=request.user)
        if edit_form.is_valid():
            user = edit_form.save()
            client.phone = edit_form.cleaned_data['phone']
            client.save()

    return render(request, 'settings.html', {'form': edit_form})


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
                'check_rooms_form': check_rooms_form,
                'room_type': room_type
            })
    else:
        check_rooms_form = forms.CheckAvailabilityForm()
    return render(request, 'room.html', {
        'check_rooms_form': check_rooms_form,
        'room_type': room_type}
                  )


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
    room = get_object_or_404(models.Rooms, id=room_id)

    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    check_in_date = datetime.datetime.strptime(check_in, '%Y-%m-%d').date()
    check_out_date = datetime.datetime.strptime(check_out, '%Y-%m-%d').date()

    nights = (check_out_date - check_in_date).days + 1

    total_price = room.price_per_night * nights

    if request.method == 'POST':
        # if not models.Bookings.objects.check_avaliable(check_in_date, check_out_date, room, room.type_name):
        #     return redirect('booking')
        book_room_form = forms.BookingForm(request.user, request.POST)
        if book_room_form.is_valid():
            book_room = book_room_form.save()
            if book_room:
                request.session['check_in_date'] = check_in_date.strftime('%d.%m.%Y')
                request.session['check_out_date'] = check_out_date.strftime('%d.%m.%Y')
                request.session['total_price'] = total_price
                request.session['room_number'] = room.room_number
                return redirect('success')
    else:
        book_room_form = forms.BookingForm(request.user)
    return render(request, 'room-booking.html', {'form': book_room_form,
                                                 'room_number': room.room_number,
                                                 'check_in_date': check_in,
                                                 'check_out_date': check_out,
                                                 'total_price': total_price
                                                 })


@login_required()
def success(request):
    check_in_date = request.session.get('check_in_date')
    check_out_date = request.session.get('check_out_date')
    total_price = request.session.get('total_price')
    room_number = request.session.get('room_number')

    if not check_in_date or not check_out_date or not total_price:
        return redirect('booking')

    # Отображаем страницу успеха
    return render(request, 'success-page.html', {
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'total_price': total_price,
        'room_number': room_number,
    })


def contacts(request):
    if request.method == 'POST':
        rating_form = forms.FeedbackForm(request.user, request.POST)
        if rating_form.is_valid():
            rating_form.save()
            messages.success(request, 'Ваш отзыв успешно отправлен! Спасибо за обратную связь.')
            return redirect('contacts')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        rating_form = forms.FeedbackForm(request.user)

    return render(request, 'contacts.html', {'form': rating_form})


def spa(request):
    return render(request, 'spa.html')
