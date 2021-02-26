from django import template
from hotelapp.models import Hotel, Guest, Receptionist
from datetime import date, timedelta

register = template.Library()


@register.simple_tag
def get_hotel():
    return Hotel.get_hotel()


@register.simple_tag
def get_today():
    today = date.today()
    return today.strftime("%Y-%m-%d")


@register.simple_tag
def get_tomorrow():
    tomorrow = date.today() + timedelta(days=1)
    return tomorrow.strftime("%Y-%m-%d")


@register.simple_tag
def get_stars():
    hotel = Hotel.get_hotel()
    if hotel is not None:
        return '&#9733' * hotel.stars
    else:
        return None


@register.simple_tag(takes_context=True)
def get_user_type(context):
    request = context['request']

    try:
        Guest.objects.get(user_ptr_id=request.user.pk)
        return 'guest'
    except Guest.DoesNotExist:
        pass

    try:
        Receptionist.objects.get(user_ptr_id=request.user.pk)
        return 'receptionist'
    except Receptionist.DoesNotExist:
        pass

    return 'other'
