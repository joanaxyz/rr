from django.core.management.base import BaseCommand
from rr_app.models import Restaurant
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Add dummy price ranges to existing restaurants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min',
            type=int,
            default=150,
            help='Minimum price range floor (default: 150)'
        )
        parser.add_argument(
            '--max',
            type=int,
            default=2500,
            help='Maximum price range ceiling (default: 2500)'
        )

    def handle(self, *args, **options):
        min_price_floor = options['min']
        max_price_ceiling = options['max']

        restaurants = Restaurant.objects.all()
        
        if not restaurants.exists():
            self.stdout.write(
                self.style.WARNING('No restaurants found in database.')
            )
            return

        updated_count = 0

        for restaurant in restaurants:
            # Generate random price_min between min_price_floor and 1000
            price_min = Decimal(str(random.randint(min_price_floor, 1000)))
            
            # Generate price_max that's higher than price_min
            # Ensure it's at least 500 more than price_min
            price_max = Decimal(str(random.randint(
                int(price_min) + 500, 
                max_price_ceiling
            )))
            
            restaurant.price_min = price_min
            restaurant.price_max = price_max
            restaurant.save()
            updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} restaurants with price ranges'
            )
        )

        # Display summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write('PRICE RANGE SUMMARY:')
        self.stdout.write('='*60)
        
        sample_restaurants = restaurants[:5]
        for restaurant in sample_restaurants:
            self.stdout.write(
                f"• {restaurant.name}: ₱{int(restaurant.price_min)} - ₱{int(restaurant.price_max)}"
            )
        
        if restaurants.count() > 5:
            self.stdout.write(f"... and {restaurants.count() - 5} more restaurants")
        
        self.stdout.write(f"\nTotal restaurants updated: {updated_count}")