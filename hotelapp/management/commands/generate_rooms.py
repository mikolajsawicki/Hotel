from hotelapp.data_generators import generate_sample_rooms
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generates sample rooms set.'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        generate_sample_rooms(options['count'])

        self.stdout.write(self.style.SUCCESS('Generated ' + str(options['count']) + ' rooms.'))
