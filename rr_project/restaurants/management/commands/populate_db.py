from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, time
from decimal import Decimal
from accounts.models import User, Customer, Admin
from restaurants.models import Restaurant, Cuisine, Tags, Review
from reservations.models import Reservation


class Command(BaseCommand):
    help = 'Populate the database with test data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting database population...'))

        # Clear existing data
        User.objects.all().delete()
        Restaurant.objects.all().delete()
        Cuisine.objects.all().delete()
        Tags.objects.all().delete()
        Review.objects.all().delete()
        Reservation.objects.all().delete()

        # Create Admin User
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='ADMIN',
            first_name='Admin',
            last_name='User'
        )
        admin_user.email_verified = True
        admin_user.save()
        Admin.objects.create(user=admin_user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created admin user: {admin_user.email}'))

        # Create Customer Users
        customers_data = [
            {'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Johnson'},
            {'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Williams'},
        ]

        customers = []
        for data in customers_data:
            user = User.objects.create_user(
                username=data['email'].split('@')[0],
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
            self.stdout.write(self.style.SUCCESS(f'✓ Created customer: {data["email"]}'))

        # Create Cuisines
        cuisine_names = ['Italian', 'Asian', 'Mexican', 'French', 'Indian', 'American']
        cuisines = {}
        for name in cuisine_names:
            cuisine = Cuisine.objects.create(name=name)
            cuisines[name] = cuisine
            self.stdout.write(self.style.SUCCESS(f'✓ Created cuisine: {name}'))

        # Create Tags
        tag_names = ['Vegetarian', 'Vegan', 'Spicy', 'Gluten-Free', 'Organic', 'Fast Service']
        tags = {}
        for name in tag_names:
            tag = Tags.objects.create(tag=name)
            tags[name] = tag
            self.stdout.write(self.style.SUCCESS(f'✓ Created tag: {name}'))

        # Create Restaurants
        restaurants_data = [
            {
                'name': 'Bella Italia',
                'street_number': '123',
                'street_name': 'Main Street',
                'street_block': 'Downtown',
                'city': 'San Francisco',
                'postal_code': '94102',
                'email': 'info@bellaitalia.com',
                'phone_number': '+1-555-0101',
                'description': 'Authentic Italian restaurant serving traditional pasta and pizza',
                'price_min': Decimal('10.00'),
                'price_max': Decimal('50.00'),
                'max_guest_count': 8,
                'opening_time': time(11, 0),
                'closing_time': time(22, 0),
                'operating_days': 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
                'cuisines': ['Italian', 'French'],
                'tags': ['Vegetarian']
            },
            {
                'name': 'Dragon Palace',
                'street_number': '456',
                'street_name': 'Oak Avenue',
                'street_block': 'Chinatown',
                'city': 'San Francisco',
                'postal_code': '94108',
                'email': 'info@dragonpalace.com',
                'phone_number': '+1-555-0102',
                'description': 'Premium Asian cuisine featuring Chinese, Japanese, and Thai dishes',
                'price_min': Decimal('12.00'),
                'price_max': Decimal('40.00'),
                'max_guest_count': 10,
                'opening_time': time(10, 30),
                'closing_time': time(23, 0),
                'operating_days': 'Tue,Wed,Thu,Fri,Sat,Sun',
                'cuisines': ['Asian'],
                'tags': ['Spicy', 'Fast Service']
            },
            {
                'name': 'Casa Mexicana',
                'street_number': '789',
                'street_name': 'Pine Street',
                'street_block': 'Riverside',
                'city': 'Oakland',
                'postal_code': '94612',
                'email': 'info@casamexicana.com',
                'phone_number': '+1-555-0103',
                'description': 'Colorful Mexican restaurant with authentic recipes and vibrant atmosphere',
                'price_min': Decimal('8.00'),
                'price_max': Decimal('35.00'),
                'max_guest_count': 10,
                'opening_time': time(11, 0),
                'closing_time': time(22, 30),
                'operating_days': 'Mon,Wed,Thu,Fri,Sat,Sun',
                'cuisines': ['Mexican'],
                'tags': ['Spicy', 'Vegetarian']
            },
            {
                'name': 'Le Gourmet',
                'street_number': '321',
                'street_name': 'Elm Street',
                'street_block': 'Uptown',
                'city': 'Berkeley',
                'postal_code': '94704',
                'email': 'info@legourmet.com',
                'phone_number': '+1-555-0104',
                'description': 'Fine dining French establishment with an extensive wine collection',
                'price_min': Decimal('25.00'),
                'price_max': Decimal('100.00'),
                'max_guest_count': 6,
                'opening_time': time(18, 0),
                'closing_time': time(23, 30),
                'operating_days': 'Wed,Thu,Fri,Sat,Sun',
                'cuisines': ['French'],
                'tags': ['Organic']
            },
            {
                'name': 'Spice Route',
                'street_number': '654',
                'street_name': 'Birch Lane',
                'street_block': 'East Side',
                'city': 'San Jose',
                'postal_code': '95110',
                'email': 'info@spiceroute.com',
                'phone_number': '+1-555-0105',
                'description': 'Indian restaurant offering dishes from various regions of India',
                'price_min': Decimal('10.00'),
                'price_max': Decimal('45.00'),
                'max_guest_count': 8,
                'opening_time': time(11, 0),
                'closing_time': time(23, 0),
                'operating_days': 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
                'cuisines': ['Indian'],
                'tags': ['Vegan', 'Gluten-Free', 'Spicy']
            },
            {
                'name': 'The Classic Grill',
                'street_number': '987',
                'street_name': 'Cedar Road',
                'street_block': 'West Side',
                'city': 'Palo Alto',
                'postal_code': '94301',
                'email': 'info@classicgrill.com',
                'phone_number': '+1-555-0106',
                'description': 'American steakhouse featuring premium cuts and classic cuisine',
                'price_min': Decimal('20.00'),
                'price_max': Decimal('80.00'),
                'max_guest_count': 10,
                'opening_time': time(17, 0),
                'closing_time': time(23, 0),
                'operating_days': 'Fri,Sat,Sun',
                'cuisines': ['American'],
                'tags': ['Fast Service']
            },
        ]

        restaurants = []
        for data in restaurants_data:
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
                operating_days=data['operating_days']
            )

            # Assign cuisines
            for cuisine_name in data['cuisines']:
                restaurant.cuisines.add(cuisines[cuisine_name])

            # Assign tags
            for tag_name in data['tags']:
                restaurant.tags.add(tags[tag_name])

            # Assign customers
            for customer in customers[:2]:  # Assign first 2 customers to each restaurant
                restaurant.customers.add(customer)

            restaurants.append(restaurant)
            self.stdout.write(self.style.SUCCESS(f'✓ Created restaurant: {data["name"]}'))

        # Create Reviews
        for idx, restaurant in enumerate(restaurants):
            for i, customer in enumerate(customers[:3]):  # 3 reviews per restaurant
                review = Review.objects.create(
                    customer=customer,
                    restaurant=restaurant,
                    rating=Decimal(str(4.0 + (i * 0.2))),  # Ratings between 4.0 and 4.4
                    comment=f'Great experience at {restaurant.name}! Food was delicious and service was excellent.'
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Created review for {restaurant.name}'))

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
                    f'✓ Created {reservation.status} reservation for {customer.user.get_full_name()}'
                ))

        self.stdout.write(self.style.SUCCESS('\n✅ Database population completed successfully!'))