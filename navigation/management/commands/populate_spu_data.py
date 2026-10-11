from django.core.management.base import BaseCommand
from navigation.models import Location, Path

class Command(BaseCommand):
    help = 'Populate SPU Central Campus data'

    def handle(self, *args, **options):
        # Create Locations
        locations = {
            'moroka': Location.objects.get_or_create(
                name='Moroka Hall of Residence',
                building_code='MOR',
                location_type='RESIDENCE',
                latitude=-28.7461,
                longitude=24.7628,
                description='Student residence at SPU Central Campus.'
            )[0],
            'c002': Location.objects.get_or_create(
                name='Building C002',
                building_code='C002',
                location_type='LECTURE_HALL',
                latitude=-28.7465,
                longitude=24.7625,
                description='Academic building with lecture halls and offices.'
            )[0],
            'pescod': Location.objects.get_or_create(
                name='William Pescod Educational Campus',
                building_code='WPEC',
                location_type='LAB',
                latitude=-28.7470,
                longitude=24.7630,
                description='Educational campus and laboratory facilities.'
            )[0],
            'library': Location.objects.get_or_create(
                name='Central Library',
                building_code='LIB',
                location_type='LIBRARY',
                latitude=-28.7455,
                longitude=24.7620,
                description='Main university library.'
            )[0],
            'cafeteria': Location.objects.get_or_create(
                name='Campus Cafeteria',
                building_code='CAF',
                location_type='CAFETERIA',
                latitude=-28.7460,
                longitude=24.7615,
                description='Dining hall for students and staff.'
            )[0],
            'admin': Location.objects.get_or_create(
                name='Administrative Office',
                building_code='ADM',
                location_type='ADMIN',
                latitude=-28.7450,
                longitude=24.7610,
                description='University administration and support services.'
            )[0],
        }

        # Create Paths (Edges)
        paths = [
            (locations['moroka'], locations['c002'], 150, 1.2),
            (locations['c002'], locations['pescod'], 200, 1.0),
            (locations['c002'], locations['library'], 300, 1.5),
            (locations['library'], locations['admin'], 100, 1.0),
            (locations['admin'], locations['cafeteria'], 250, 2.0), # High crowd area
            (locations['cafeteria'], locations['moroka'], 180, 1.1),
            (locations['pescod'], locations['library'], 400, 1.0),
        ]

        for start, end, dist, crowd in paths:
            Path.objects.get_or_create(
                start_location=start,
                end_location=end,
                defaults={'distance': dist, 'crowd_level': crowd}
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated SPU Central Campus data'))
