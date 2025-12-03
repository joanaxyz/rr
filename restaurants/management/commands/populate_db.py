from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, time
from decimal import Decimal
from accounts.models import User, Customer, Owner
from restaurants.models import Restaurant, Cuisine, Tags, Review, Element, Table, Floorplan
from reservations.models import Reservation


class Command(BaseCommand):
    help = 'Populate the database with Cebu City restaurant test data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting database population...'))

        # Clear existing data
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        try:
            Table.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('[OK] Cleared tables'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'[!] Could not clear tables: {e}'))
        
        try:
            Element.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('[OK] Cleared elements'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'[!] Could not clear elements: {e}'))
        
        Review.objects.all().delete()
        Reservation.objects.all().delete()
        try:
            Restaurant.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('[OK] Cleared restaurants'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'[!] Could not clear restaurants: {e}'))
        Cuisine.objects.all().delete()
        Tags.objects.all().delete()
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('[OK] Existing data cleared'))

        # Create Owner Users for restaurants
        owner_data = [
            {'email': 'owner1@cebu.com', 'first_name': 'Maria', 'last_name': 'Santos'},
            {'email': 'owner2@cebu.com', 'first_name': 'Juan', 'last_name': 'Dela Cruz'},
            {'email': 'owner3@cebu.com', 'first_name': 'Rosa', 'last_name': 'Garcia'},
            {'email': 'owner4@cebu.com', 'first_name': 'Pedro', 'last_name': 'Lopez'},
            {'email': 'owner5@cebu.com', 'first_name': 'Ana', 'last_name': 'Martinez'},
            {'email': 'owner6@cebu.com', 'first_name': 'Luis', 'last_name': 'Rodriguez'},
        ]

        owners = []
        for data in owner_data:
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password='owner123',
                role='OWNER',
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            user.email_verified = True
            user.save()
            owner = Owner.objects.create(user=user)
            owners.append(owner)
            self.stdout.write(self.style.SUCCESS(f'[OK] Created owner: {data["email"]}'))

        # Create Customer Users
        customers_data = [
            {'email': 'marco@cebu.com', 'first_name': 'Marco', 'last_name': 'Fernandez'},
            {'email': 'clara@cebu.com', 'first_name': 'Clara', 'last_name': 'Reyes'},
            {'email': 'miguel@cebu.com', 'first_name': 'Miguel', 'last_name': 'Aquino'},
            {'email': 'santos@cebu.com', 'first_name': 'Santos', 'last_name': 'Villanueva'},
            {'email': 'sofia@cebu.com', 'first_name': 'Sofia', 'last_name': 'Corpuz'},
        ]

        customers = []
        for data in customers_data:
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password='customer123',
                role='CUSTOMER',
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            user.email_verified = True
            user.save()
            customer = Customer.objects.create(user=user)
            customers.append(customer)
            self.stdout.write(self.style.SUCCESS(f'[OK] Created customer: {data["email"]}'))

        # Create Cuisines (including Cebu City specific cuisines)
        cuisine_names = ['Filipino', 'Asian', 'Seafood', 'Fusion', 'Japanese', 'Korean', 'International', 'Italian', 'Spanish', 'Mexican', 'French', 'Indian', 'American']
        cuisines = {}
        for name in cuisine_names:
            cuisine = Cuisine.objects.create(name=name)
            cuisines[name] = cuisine
            self.stdout.write(self.style.SUCCESS(f'[OK] Created cuisine: {name}'))

        # Create Tags
        tag_names = ['Vegetarian', 'Vegan', 'Spicy', 'Gluten-Free', 'Organic', 'Fast Service', 'Fresh', 'Fine Dining', 'Romantic', 'Scenic', 'Cozy']
        tags = {}
        for name in tag_names:
            tag = Tags.objects.create(tag=name)
            tags[name] = tag
            self.stdout.write(self.style.SUCCESS(f'[OK] Created tag: {name}'))

        # Create Restaurants (Cebu City based)
        restaurants_data = [
            {
                'name': 'Larsian Grill Station',
                'street_number': '456',
                'street_name': 'Larsian Street',
                'street_block': 'Carbon',
                'city': 'Cebu City',
                'postal_code': '6000',
                'email': 'info@larsiangrill.com',
                'phone_number': '+63-32-255-0101',
                'description': 'Famous Cebu lechon and grilled dishes. A must-try for authentic local flavors.',
                'price_min': Decimal('150.00'),
                'price_max': Decimal('600.00'),
                'max_guest_count': 12,
                'opening_time': time(10, 0),
                'closing_time': time(22, 0),
                'operating_days': 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
                'cuisines': ['Filipino', 'Asian'],
                'tags': ['Spicy', 'Fast Service']
            },
            {
                'name': 'Sutukil by the Waterfront',
                'street_number': '123',
                'street_name': 'Mangga Avenue',
                'street_block': 'South Road',
                'city': 'Cebu City',
                'postal_code': '6000',
                'email': 'info@sutukil.com',
                'phone_number': '+63-32-255-0102',
                'description': 'Specialty seafood restaurant offering Sutukil (sinigang, tuyo, kilawin). Enjoy fresh catch with scenic views.',
                'price_min': Decimal('200.00'),
                'price_max': Decimal('800.00'),
                'max_guest_count': 10,
                'opening_time': time(11, 0),
                'closing_time': time(23, 0),
                'operating_days': 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
                'cuisines': ['Seafood', 'Filipino'],
                'tags': ['Fresh', 'Organic']
            },
            {
                'name': 'Handuraw Tapas & Wine Bar',
                'street_number': '789',
                'street_name': 'Osmeña Boulevard',
                'street_block': 'Uptown Cebu',
                'city': 'Cebu City',
                'postal_code': '6000',
                'email': 'info@handuraw.com',
                'phone_number': '+63-32-255-0103',
                'description': 'Modern fusion restaurant combining local ingredients with international techniques. Perfect for wine enthusiasts.',
                'price_min': Decimal('300.00'),
                'price_max': Decimal('1200.00'),
                'max_guest_count': 8,
                'opening_time': time(17, 0),
                'closing_time': time(23, 30),
                'operating_days': 'Tue,Wed,Thu,Fri,Sat,Sun',
                'cuisines': ['Fusion', 'Filipino'],
                'tags': ['Fine Dining', 'Organic']
            },
            {
                'name': 'Choobi Choobi',
                'street_number': '234',
                'street_name': 'Jones Avenue',
                'street_block': 'Mabolo',
                'city': 'Cebu City',
                'postal_code': '6000',
                'email': 'info@choobichoobi.com',
                'phone_number': '+63-32-255-0104',
                'description': 'Japanese-Korean fusion restaurant with authentic ramen, BBQ, and Korean dishes.',
                'price_min': Decimal('180.00'),
                'price_max': Decimal('700.00'),
                'max_guest_count': 10,
                'opening_time': time(11, 0),
                'closing_time': time(22, 0),
                'operating_days': 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
                'cuisines': ['Japanese', 'Korean'],
                'tags': ['Spicy', 'Fast Service']
            },
            {
                'name': 'Golden Cowrie Beach Club',
                'street_number': '567',
                'street_name': 'A.S. Fortuna Street',
                'street_block': 'Banilad',
                'city': 'Cebu City',
                'postal_code': '6000',
                'email': 'info@goldencowrie.com',
                'phone_number': '+63-32-255-0105',
                'description': 'Beachfront dining experience with international and local cuisine. Great ambiance for gatherings.',
                'price_min': Decimal('250.00'),
                'price_max': Decimal('900.00'),
                'max_guest_count': 14,
                'opening_time': time(11, 0),
                'closing_time': time(23, 0),
                'operating_days': 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
                'cuisines': ['International', 'Seafood'],
                'tags': ['Romantic', 'Scenic']
            },
            {
                'name': 'Casa Cortes Cafe',
                'street_number': '345',
                'street_name': 'Sanciangko Street',
                'street_block': 'South Road',
                'city': 'Cebu City',
                'postal_code': '6000',
                'email': 'info@casacortes.com',
                'phone_number': '+63-32-255-0106',
                'description': 'Cozy Italian-Spanish cafe with pasta, tapas, and premium coffee. Perfect for lunch and coffee lovers.',
                'price_min': Decimal('120.00'),
                'price_max': Decimal('400.00'),
                'max_guest_count': 8,
                'opening_time': time(8, 0),
                'closing_time': time(21, 0),
                'operating_days': 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
                'cuisines': ['Italian', 'Spanish'],
                'tags': ['Vegetarian', 'Cozy']
            },
        ]

        restaurants = []
        for idx, data in enumerate(restaurants_data):
            # Assign owner (cycle through owners)
            owner = owners[idx % len(owners)]
            
            restaurant = Restaurant.objects.create(
                name=data['name'],
                street_number=data['street_number'],
                street_name=data['street_name'],
                street_block=data['street_block'],
                city=data['city'],
                postal_code=data['postal_code'],
                email=data['email'],
                phone_number=data['phone_number'],
                description=data['description'],
                price_min=data['price_min'],
                price_max=data['price_max'],
                max_guest_count=data['max_guest_count'],
                opening_time=data['opening_time'],
                closing_time=data['closing_time'],
                operating_days=data['operating_days'],
                owner=owner
            )

            # Assign cuisines
            for cuisine_name in data['cuisines']:
                if cuisine_name in cuisines:
                    restaurant.cuisines.add(cuisines[cuisine_name])

            # Assign tags
            for tag_name in data['tags']:
                if tag_name in tags:
                    restaurant.tags.add(tags[tag_name])

            # Assign customers
            for customer in customers[:2]:  # Assign first 2 customers to each restaurant
                restaurant.customers.add(customer)

            restaurants.append(restaurant)
            self.stdout.write(self.style.SUCCESS(f'[OK] Created restaurant: {data["name"]} (Owner: {owner.user.email})'))

        # Create Reviews
        for idx, restaurant in enumerate(restaurants):
            for i, customer in enumerate(customers[:3]):  # 3 reviews per restaurant
                review = Review.objects.create(
                    customer=customer,
                    restaurant=restaurant,
                    rating=Decimal(str(4.0 + (i * 0.2))),  # Ratings between 4.0 and 4.4
                    comment=f'Great experience at {restaurant.name}! Food was delicious and service was excellent.'
                )
                self.stdout.write(self.style.SUCCESS(f'[OK] Created review for {restaurant.name}'))

        # Create Floorplans and Elements for each restaurant
        try:
            element_names = ['Window', 'Bar', 'Entrance', 'Kitchen', 'Restroom', 'Storage']
            elements_created = 0
            for restaurant in restaurants:
                floorplan = Floorplan.objects.create(
                    restaurant=restaurant,
                    width=Decimal('1000.00'),
                    height=Decimal('600.00')
                )
                for idx, element_name in enumerate(element_names):  # All elements per restaurant
                    element = Element.objects.create(
                        name=element_name,
                        x=Decimal('50') + Decimal(idx * 100),
                        y=Decimal('50') + Decimal(idx * 75),
                        width=Decimal('100.00'),
                        height=Decimal('80.00'),
                        floorplan=floorplan
                    )
                    elements_created += 1
                    self.stdout.write(self.style.SUCCESS(f'[OK] Created element "{element_name}" for {restaurant.name}'))
            self.stdout.write(self.style.SUCCESS(f'[OK] Total elements created: {elements_created}'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'[!] Could not create elements: {str(e)[:100]}'))

        # Create Tables for each restaurant
        try:
            table_configs = [
                {'capacity': 2, 'count': 4},   # 4 tables for 2 people
                {'capacity': 4, 'count': 3},   # 3 tables for 4 people
                {'capacity': 6, 'count': 2},   # 2 tables for 6 people
                {'capacity': 8, 'count': 1},   # 1 large table for 8 people
            ]

            tables_created = 0
            for restaurant in restaurants:
                floorplan = Floorplan.objects.get(restaurant=restaurant)
                table_number = 1
                for config in table_configs:
                    for i in range(config['count']):
                        table = Table.objects.create(
                            number=table_number,
                            capacity=config['capacity'],
                            x=50 + (i * 200),
                            y=100 + (config['capacity'] * 50),
                            floorplan=floorplan,
                            status='available'
                        )
                        table_number += 1
                        tables_created += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'[OK] Created table #{table.number} (capacity {table.capacity}) for {restaurant.name}'
                        ))
            self.stdout.write(self.style.SUCCESS(f'[OK] Total tables created: {tables_created}'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'[!] Could not create tables: {str(e)[:100]}'))

        # Create Reservations
        for idx, customer in enumerate(customers):
            for res_idx in range(2):  # 2 reservations per customer
                reservation = Reservation.objects.create(
                    customer=customer,
                    restaurant=restaurants[idx % len(restaurants)],
                    name=customer.user.get_full_name(),
                    email=customer.user.email,
                    guest_count=2 + res_idx,
                    date=timezone.now().date(),
                    time=time(19 + res_idx, 0),
                    notes=f'Special request for reservation #{res_idx + 1}',
                    status='CONFIRMED' if res_idx == 0 else 'PENDING'
                )
                self.stdout.write(self.style.SUCCESS(
                    f'[OK] Created {reservation.status} reservation for {customer.user.get_full_name()}'
                ))

        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Database population completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(owners)} Owners'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(customers)} Customers'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(restaurants)} Restaurants'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(restaurants) * 6} Elements (Window, Bar, Entrance, Kitchen, Restroom, Storage)'))
        self.stdout.write(self.style.SUCCESS(f'  - {sum(config["count"] for config in table_configs) * len(restaurants)} Tables'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(restaurants) * 3} Reviews'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(customers) * 2} Reservations'))