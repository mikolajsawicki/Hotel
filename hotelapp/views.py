from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import IntegrityError

from .period import DateRangeException, Period

from .models import *

from django.core.validators import validate_integer

from .templatetags.custom_tags import get_today, get_tomorrow


def index(request):
    context = dict()

    try:
        hotel = Hotel.get_hotel()
        context['hotel_images'] = hotel.images.all()
    except Hotel.DoesNotExist:
        pass

    return render(request, 'hotelapp/index.html', context)


def get_rooms_available_in(rooms, period):
    rooms_available = []
    for r in rooms:
        room_reservations = ReservationActive.objects.filter(room=r)

        colliding_reservations = [res for res in room_reservations if period.overlaps(res.period())]

        if not colliding_reservations:
            rooms_available.append(r)

    return rooms_available


def search_rooms(request):
    context = dict()

    context['errors'] = []
    context['date_start'] = request.POST.get('date_start', get_today())
    context['date_end'] = request.POST.get('date_end', get_tomorrow())
    context['guests_count'] = request.POST.get('guests_count')

    try:
        guests_count = request.POST['guests_count']

        validate_integer(guests_count)

        rooms_to_show = Room.objects.filter(guests_count__gte=guests_count).order_by('guests_count')
    except (KeyError, ValidationError):
        rooms_to_show = Room.objects.all()

    try:
        period = Period(
            datetime.strptime(request.POST['date_start'], '%Y-%m-%d').date(),
            datetime.strptime(request.POST['date_end'], '%Y-%m-%d').date()
        )
        rooms_to_show = get_rooms_available_in(rooms_to_show, period)
    except KeyError:
        pass
    except DateRangeException:
        context['errors'].append('Start date has to be before end date')

    context['rooms'] = rooms_to_show

    return render(request, 'hotelapp/rooms.html', context)


def room_view(request, room_id):
    context = {
        'room': get_object_or_404(Room, pk=room_id)
    }

    context['date_start'] = request.POST.get('date_start', get_today())
    context['date_end'] = request.POST.get('date_end', get_tomorrow())

    context['guests_count'] = request.POST.get('guests_count')

    return render(request, 'hotelapp/room.html', context)


def guest_register(request):
    context = {
        'errors': []
    }

    try:
        Guest.objects.get(email=request.POST['email'])
        context['errors'].append('The user with that email already exists. Try to log in.')
    except Guest.DoesNotExist:
        try:
            guest = Guest.objects.create_user(
                username=request.POST['email'],
                email=request.POST['email'],
                password=request.POST['password'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name']
            )
        except KeyError:
            context['errors'].append('You should fill all required data.')
            return render(request, 'hotelapp/register.html')

        try:
            guest.phone_number = request.POST['phone_number']
            guest.save()
        except KeyError:
            pass

        return redirect(reverse('hotelapp:login'))
    except KeyError:
        pass

    return render(request, 'hotelapp/register.html', context)


def guest_login(request):
    context = {
        'errors': []
    }

    try:
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect(reverse('hotelapp:rooms'))

        except (User.DoesNotExist):
            pass

        context['errors'].append('Bad credentials')

    except KeyError:
        pass

    return render(request, 'hotelapp/login.html', context)


def guest_logout(request):
    logout(request)
    return redirect(reverse('hotelapp:index'))


def guest_add_reservation(request):
    if not request.user.is_authenticated:
        request.session['reservation_quited'] = request.POST
        return redirect(reverse('hotelapp:login'))

    context = {
        'errors': [],
        'successes': []
    }

    try:
        room = Room.objects.get(pk=request.POST.get('room_id'))
    except (Room.DoesNotExist, ValueError):
        return redirect(reverse('hotelapp:index'))

    try:
        to_date = lambda s: datetime.strptime(s, '%Y-%m-%d').date()
        date_start = to_date(request.POST.get('date_start'))
        date_end = to_date(request.POST.get('date_end'))
        period = Period(date_start, date_end)
    except (DateRangeException, TypeError):
        return redirect(reverse('hotelapp:index'))

    guests_count = int(request.POST.get('guests_count'))

    if request.POST.get('confirmed', 0) == '1':
        try:
            try:
                res = ReservationActive(
                    room=room,
                    guest=Guest.objects.get(user_ptr_id=request.user.pk),
                    start_date=period.start,
                    end_date=period.end,
                    guests_count=guests_count
                )
                res.save()
                return redirect(reverse('hotelapp:my_reservations'))

            except DateNotAvailableException:
                context['errors'].append('Room is not available in this period.')
            except TooMuchGuestsException:
                context['errors'].append('Too much guests for this room.')
            except Guest.DoesNotExist:
                context['errors'].append('You are not a guest.')


        except KeyError:
            context['errors'].append('You did not fill all the required data')

    context['room'] = room
    context['date_start'] = date_start.strftime("%Y-%m-%d") if date_start is not None else get_today()
    context['date_end'] = date_end.strftime("%Y-%m-%d") if date_end is not None else get_tomorrow()
    context['guests_count'] = guests_count if guests_count is not None else room.guests_count

    return render(request, 'hotelapp/add_reservation.html', context)


def my_reservations(request):
    if not request.user.is_authenticated:
        return redirect(reverse('hotelapp:login'))

    try:
        Guest.objects.get(user_ptr_id=request.user.pk)
    except Guest.DoesNotExist:
        return redirect(reverse('hotelapp:login'))

    context = dict()

    try:
        guest = Guest.objects.get(user_ptr_id=request.user.pk)
        context['reservations'] = ReservationActive.objects.filter(guest=guest)
    except Guest.DoesNotExist:
        return redirect(reverse('hotelapp:index'))

    return render(request, 'hotelapp/my_reservations.html', context)


def manage_reservations(request):
    if not request.user.is_authenticated:
        return redirect(reverse('hotelapp:login'))

    try:
        Receptionist.objects.get(user_ptr_id=request.user.pk)
    except Receptionist.DoesNotExist:
        if not request.user.is_superuser:
            return redirect(reverse('hotelapp:login'))
        pass

    reservations = ReservationActive.objects.all()

    try:
        guest_id = int(request.GET['guest_id'])
        reservations.filter(guest=Guest.objects.get(pk=guest_id))
    except KeyError:
        pass

    context = {
        'reservations': reservations,
        'errors': [],
        'successes': []
    }

    if request.POST.get('form_sent', 0) == '1':
        try:
            reservation = ReservationActive.objects.get(pk=int(request.POST.get('reservation_id')))
            guests_count = int(request.POST.get('guests_count'))
            payment_status = True if request.POST.get('payment_status') == 'paid' else False

            reservation.guests_count = guests_count
            reservation.payment_status = payment_status

            reservation.save()

            context['successes'].append('The reservation has been modified.')

        except ReservationActive.DoesNotExist:
            context['errors'].append('Reservation does not exist.')

    return render(request, 'hotelapp/manage_reservations.html', context)


def manage_guests(request):
    if not request.user.is_authenticated:
        return redirect(reverse('hotelapp:login'))

    try:
        Receptionist.objects.get(user_ptr_id=request.user.pk)
    except Receptionist.DoesNotExist:
        if not request.user.is_superuser:
            return redirect(reverse('hotelapp:login'))
        pass

    context = {
        'guests': Guest.objects.all(),
        'errors': [],
        'successes': []
    }

    if request.POST.get('form_sent', 0) == '1':
        try:
            guest = Guest.objects.get(pk=int(request.POST.get('guest_id')))
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')

            guest.first_name = first_name
            guest.last_name = last_name
            guest.username = email
            guest.email = email
            guest.phone_number = phone_number

            guest.save()

            context['successes'].append('The guest has been modified.')

        except Guest.DoesNotExist:
            context['errors'].append('Guest does not exist.')
        except IntegrityError:
            context['errors'].append('This email is not available.')


    return render(request, 'hotelapp/manage_guests.html', context)

def statistics(request):
    if not request.user.is_authenticated:
        return redirect(reverse('hotelapp:login'))

    if not request.user.is_superuser:
        return redirect(reverse('hotelapp:login'))

    context = dict()
    context['errors'] = []
    context['guests_count'] = Guest.objects.all().count()
    context['receptionists_count'] = Receptionist.objects.all().count()

    try:
        date_start = request.POST['date_start']
        date_end = request.POST['date_end']
        period = Period(
            datetime.strptime(date_start, '%Y-%m-%d').date(),
            datetime.strptime(date_end, '%Y-%m-%d').date()
        )
        context['income'] = Reservation.income(period)
        context['date_start'] = date_start
        context['date_end'] = date_end
    except KeyError:
        pass
    except DateRangeException:
        context['errors'].append('Start date has to be before end date')


    return render(request, 'hotelapp/statistics.html', context)