from hotelapp.data_generators import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generates sample hotel data.'

    def handle(self, *args, **options):
        generate_sample_hotel()
        self.stdout.write(self.style.SUCCESS('The hotel has been generated.'))
        generate_sample_rooms(15)
        self.stdout.write(self.style.SUCCESS('The hotel rooms have been generated.'))
        generate_sample_guests(20)
        self.stdout.write(self.style.SUCCESS('The guests have been generated.'))
        generate_sample_receptionists(5)
        self.stdout.write(self.style.SUCCESS('The receptionists have been generated.'))
        generate_sample_reservations_active(30)
        self.stdout.write(self.style.SUCCESS('The active reservations have been generated.'))
        self.stdout.write(self.style.SUCCESS('Done.'))
