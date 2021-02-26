# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .period import Period


class User(AbstractUser):
    pass


class Guest(User):
    phone_number = models.CharField(max_length=255, default=None, blank=True, null=True)

    def has_perm(self, perm, obj=None):
        if perm == 'add_reservation_for_self':
            return True

        return False


class Receptionist(User):
    phone_number = models.CharField(max_length=255, default=None, blank=True, null=True)
    pesel = models.CharField(max_length=11, default=None, blank=True, null=True)
    address = models.CharField(max_length=255, default=None, blank=True, null=True)


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024, default=None, blank=True, null=True)
    stars = models.IntegerField(default=None, blank=True, null=True)
    localization = models.CharField(max_length=1024, default=None, blank=True, null=True)
    email = models.CharField(max_length=255, default=None, blank=True, null=True)
    phone_number = models.CharField(max_length=64, default=None, blank=True, null=True)

    @staticmethod
    def get_hotel():
        try:
            return Hotel.objects.all()[0]
        except (IndexError, Hotel.DoesNotExist):
            return None


class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField()

    @property
    def url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url


class Room(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024, default=None, blank=True, null=True)
    room_number = models.IntegerField()
    price_for_night = models.IntegerField()
    guests_count = models.IntegerField()
    photo = models.ImageField(upload_to='images/rooms', default=None, blank=True, null=True)


class DateNotAvailableException(Exception):
    pass


class TooMuchGuestsException(Exception):
    pass


class Reservation(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    creation_date = models.DateField()
    creation_time = models.TimeField()
    payment_status = models.BooleanField(default=False)
    bill = models.IntegerField()
    guests_count = models.IntegerField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)

    def period(self):
        return Period(self.start_date, self.end_date)

    def period_available(self):
        reservations = ReservationActive.objects.filter(room=self.room).exclude(pk=self.pk)

        for r in reservations:
            if self.period().overlaps(r.period()):
                return False

        return True

    @staticmethod
    def income(period):
        reservations = Reservation.objects.all()

        income = 0

        for r in reservations:
            if r.start_date >= period.start and r.end_date <= period.end:
                income = income + r.bill

        return income


class ReservationActive(Reservation):
    def save(self, *args, **kwargs):
        if not self.period_available():
            raise DateNotAvailableException('Date not available.')

        if self.guests_count > self.room.guests_count:
            raise TooMuchGuestsException('Too much guests for this room.')

        self.creation_date = timezone.now().date()
        self.creation_time = timezone.now().time()

        self.bill = (self.period().length().days - 1) * self.room.price_for_night

        super().save(*args, **kwargs)

    class Meta:
        permissions = [
            ("add_reservation_for_self", "Can add reservation for self"),
            ("change_payment_status", "Can change reservation's payment status"),
            ("deactivate", "Can deactivate reservation"),
        ]


class ReservationInactive(Reservation):
    pass
