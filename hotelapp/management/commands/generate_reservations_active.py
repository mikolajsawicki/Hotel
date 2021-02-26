from hotelapp.data_generators import generate_sample_reservations_active
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """Generates sample reservation between two dates. 
              Example: generate_reservations_active "2000-05-24" "2000-05-26" """

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        generate_sample_reservations_active(options['count'])

        self.stdout.write(self.style.SUCCESS('The reservation has been generated.'))
