import random

from django.templatetags.static import static

from .models import *
from datetime import datetime, timedelta

def generate_sample_reservation(date_start, date_end):
    rooms = list(Room.objects.all())
    random_room = random.sample(rooms, 1)[0]

    res = ReservationActive(start_date=date_start, end_date=date_end,
                            guests_count=random.randint(1, random_room.guests_count), room=random_room,
                            guest=random.sample(list(Guest.objects.all()), 1)[0])
    res.save()


def generate_sample_reservations_active(count):
    for i in range(count):
        datetime_start = datetime.now() + timedelta(days=random.randint(1, 1000))
        date_start = datetime_start.date()
        date_end = (datetime_start + timedelta(days=random.randint(1, 5))).date()

        try:
            generate_sample_reservation(date_start, date_end)
        except DateNotAvailableException:
            i = i - 1


def phone_number():
    for i in range(100000000, 999999999):
        yield str(i)


def mail():
    i = 0
    while True:
        yield "mail%s@example.com" % i
        i = i + 1


def pesel():
    for i in range(10000000000, 99999999999):
        yield str(i)


first_names = ("Jacek", "Sergiusz", "Krzysztof", "Amelia", "Łukasz")
last_names = ("Kowalski", "Potocki", "Rosicki", "Benua")
passwords = ("SuPERsilnEHaslo12&", "aleHasloo34521^%1gfdD", "FDShaefsdvxcSDF342@g%342f#s", "do2bre1Haslo342*&3")
addresses = ("""ul. Cicha 132 m. 16
                            62-200 GNIEZNO
                            POLSKA[b]""",
             """Mnichowo 132
                     62-200 MNICHOWO
                     POLSKA""",
             """ul. Jakaś 22
                     67-452 SOSNOWIEC
                     POLSKA""",
             """ ul. Inna 55
                     62-200 KARPACZ
                     POLSKA"""
             """Some Beautiful Street 420
                     62-200 SAN FRANCISCO
                     STANY ZJEDNOCZONE""")


def generate_sample_guests(count):
    phones = phone_number()
    mails = mail()

    i = 0

    while i < count:
        m = next(mails)

        try:
            user = User.objects.get(username=m)
        except User.DoesNotExist:
            user = Guest.objects.create_user(m, m, random.sample(passwords, 1)[0])
            user.first_name = random.sample(first_names, 1)[0]
            user.last_name = random.sample(last_names, 1)[0]
            user.phone_number = next(phones)
            user.save()
            i = i + 1


def generate_sample_receptionists(count):
    phones = phone_number()
    mails = mail()
    pesels = pesel()

    i = 0

    while i < count:
        m = next(mails)

        try:
            user = User.objects.get(username=m)
        except User.DoesNotExist:
            user = Receptionist.objects.create_user(m, m, random.sample(passwords, 1)[0])
            user.first_name = random.sample(first_names, 1)[0]
            user.last_name = random.sample(last_names, 1)[0]
            user.phone_number = next(phones)
            user.pesel = next(pesels)
            user.address = random.sample(addresses, 1)[0]
            user.save()
            i = i + 1


def room_number():
    i = 0
    while True:
        yield i
        i = i + 1


def price_for_night():
    while True:
        yield random.randint(10000, 40000)


def generate_sample_rooms(count):
    room_numbers = room_number()
    prices = price_for_night()

    # sets of name, description and guests count
    ndg = (("Przestronny apartament", "Pełen przestrzeni apartament. Bogato wyposażony.", 4),
           ("Pokój rodzinny", "Pokój idealny dla rodziny z dziećmi - wypełniony ciepłą atmosferą.", 6),
           ("Apartament na poddaszu", "Klimatyczny pokój usytuowany na poddaszu.", 4),
           ("Pokój dla pary", "Romantyczny pokój idealny dla pary.", 2),
           ("Pokój dla rodziny z dziećmi", "Pokój idealny dla rodziny z dziećmi.", 5))

    for i in range(count):
        dataset = random.sample(ndg, 1)[0]

        room = Room(name=dataset[0], description=dataset[1], room_number=next(room_numbers),
                    price_for_night=next(prices), guests_count=dataset[2], photo='sample_room.jpg')

        room.save()


def generate_sample_hotel():
    hotel = Hotel(name="Hotel Paradajs", description="Urokliwy hotel Paradajs w słonecznym Karpaczu.",
                  localization="Wiśniowa 3, 58-540 Karpacz",
                  phone_number="646999999", email="hotel@paradajs.pl", stars=5)

    hotel.save()
