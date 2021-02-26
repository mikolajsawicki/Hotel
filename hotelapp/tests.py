from datetime import datetime
from urllib.request import Request

from django.contrib.auth.hashers import check_password
from django.test import TestCase, Client
from django.urls import reverse

from .data_generators import generate_sample_rooms, generate_sample_reservation, generate_sample_guests
from .models import *


def str_to_date(s):
    return datetime.strptime(s, '%Y-%m-%d').date()


class PeriodTestsDateRangesOverlap(TestCase):

    def test_periods_overlap(self):
        """
        period.overlap() returns True if  p1 overlaps p2 or False if doesn't.
        """

        tests = (
            ['2020-06-27', '2020-06-28', '2020-07-27', '2020-07-28', False],
            ['2020-06-01', '2020-07-03', '2020-07-02', '2020-07-04', True],
            ['2020-06-02', '2020-06-03', '2020-06-01', '2020-06-04', True],
            ['2020-06-02', '2020-07-04', '2020-07-01', '2020-07-03', True],
            ['2020-06-27', '2020-06-28', '2020-07-27', '2020-07-28', False],
        )

        dataset = [dict(zip(['1_start', '1_end', '2_start', '2_end', 'overlaps'], d)) for d in tests]

        for data in dataset:
            p1 = Period(data['1_start'], data['1_end'])
            p2 = Period(data['2_start'], data['2_end'])
            self.assertIs(p1.overlaps(p2), data['overlaps'])


class ReservationsActiveModelTests(TestCase):

    def test_reservation_collides(self):
        """
        date_range_available() should raise DateNotAvailableException for colliding dates
        """
        generate_sample_rooms(1)
        generate_sample_guests(3)

        try:
            generate_sample_reservation(str_to_date('2020-06-27'), str_to_date('2020-06-29'))
            generate_sample_reservation(str_to_date('2020-06-28'), str_to_date('2020-06-30'))
            self.assertIs(True, False)
        except DateNotAvailableException:
            pass


class GuestRegisterViewTests(TestCase):

    def test_register_all_data(self):
        """
        register() should register a valid user for full set of: email, password, firstname, lastname and phone number
        """
        post_data = {'email': 'mail@example.com',
                     'password': 'strongPASSWor123fD@#sD',
                     'first_name': 'Johny',
                     'last_name': 'Depp',
                     'phone_number': '777777777'}

        response = self.client.post(reverse('hotelapp:register'), post_data)

        self.assertEqual(response.status_code, 302)

        try:
            user = Guest.objects.get(email=post_data['email'])
            self.assertEqual(user.email, post_data['email'])
            self.assertEqual(check_password(post_data['password'], user.password), True)
            self.assertEqual(user.first_name, post_data['first_name'])
            self.assertEqual(user.last_name, post_data['last_name'])
            self.assertEqual(user.phone_number, post_data['phone_number'])
        except User.DoesNotExist:
            self.assertIs(True, False)



    def test_register_all_data_except_phone_number(self):
        """
        register() should register a valid user for set of: email, password, firstname, lastname
        """
        post_data = {   'email': 'mail@example.com',
                        'password': 'strongPASSWor123fD@#sD',
                        'first_name': 'Johny',
                        'last_name': 'Depp'}

        response = self.client.post(reverse('hotelapp:register'), post_data)

        self.assertEqual(response.status_code, 302)

        try:
            user = Guest.objects.get(email=post_data['email'])
            self.assertEqual(user.email, post_data['email'])
            self.assertEqual(check_password(post_data['password'], user.password), True)
            self.assertEqual(user.first_name, post_data['first_name'])
            self.assertEqual(user.last_name, post_data['last_name'])
            self.assertEqual(user.phone_number, None)
        except User.DoesNotExist:
            self.assertIs(True, False)

    def test_register_all_data_except_password(self):
        """
        register() should not register an user for set of: email, first_name, lastname and phone number
        """
        post_data = {'email': 'mail@example.com',
                     'first_name': 'Johny',
                     'last_name': 'Depp',
                     'phone_number': '777777777'}

        response = self.client.post(reverse('hotelapp:register'), post_data)

        self.assertNotEqual(response.status_code, 302)

        try:
            user = Guest.objects.get(email=post_data['email'])
            self.assertIs(True, False)
        except User.DoesNotExist:
            pass

        def test_register_all_data_except_first_name(self):
            """
            register() should not register an user for set of: email, password, lastname and phone number
            """
            post_data = {'email': 'mail@example.com',
                         'password': 'strongPASSWor123fD@#sD',
                         'last_name': 'Depp',
                         'phone_number': '777777777'}

            response = self.client.post(reverse('hotelapp:register'), post_data)

            self.assertNotEqual(response.status_code, 302)

            try:
                Guest.objects.get(email=post_data['email'])
                self.assertIs(True, False)
            except User.DoesNotExist:
                pass

    def test_register_all_data_except_last_name(self):
        """
        register() should not register an user for set of: email, password, firstname and phone number
        """
        post_data = {'email': 'mail@example.com',
                     'password': 'strongPASSWor123fD@#sD',
                     'first_name': 'Johny',
                     'phone_number': '777777777'}

        response = self.client.post(reverse('hotelapp:register'), post_data)

        self.assertNotEqual(response.status_code, 302)

        try:
            Guest.objects.get(email=post_data['email'])
            self.assertIs(True, False)
        except Guest.DoesNotExist:
            pass

"""
class GuestAddReservationViewTests(TestCase):
    client_class = TestGuest

    def test_guest_add_reservation_valid(self):
        
        guest_add_reservation() should add a reservation for room_id, date_start, date_end and guests_count
        
        generate_sample_rooms(1)

        r = Room.objects.all()[0]

        post_data = {
            'room_id': str(r.pk),
            'date_start': '2021-04-06',
            'date_end': '2021-04-08',
            'guests_count': str(r.guests_count)
        }

        response = self.client.post(reverse('hotelapp:guest_add_reservation'), post_data, follow=True)
        print(response.content)

        self.assertEqual(response.status_code, 302)

        try:
            Reservation.objects.get(
                room=r,
                start_date=str_to_date(post_data['date_start']),
                end_date=str_to_date(post_data['date_end']),
                guests_count=r.guests_count
            )
        except Reservation.DoesNotExist:
            self.assertIs(True, False)
"""