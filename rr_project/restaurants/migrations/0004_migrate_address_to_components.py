# Generated migration to parse legacy address and populate components

from django.db import migrations


def parse_and_populate_addresses(apps, schema_editor):
    """Parse legacy address field and populate component fields"""
    Restaurant = apps.get_model('restaurants', 'Restaurant')
    
    for restaurant in Restaurant.objects.all():
        if not restaurant.address:
            continue
        
        # Skip if components are already populated
        if any([restaurant.city, restaurant.street_block, restaurant.street_name, 
                restaurant.street_number, restaurant.postal_code]):
            continue
        
        # Parse address - assuming format: "Street#, StreetName, Block, City, PostalCode"
        # or other variations like "City" or "City, PostalCode"
        parts = [p.strip() for p in restaurant.address.split(',')]
        
        # Try to intelligently assign parts
        if len(parts) >= 5:
            restaurant.street_number = parts[0]
            restaurant.street_name = parts[1]
            restaurant.street_block = parts[2]
            restaurant.city = parts[3]
            restaurant.postal_code = parts[4]
        elif len(parts) == 4:
            # Could be: Street#, StreetName, Block, City
            # or: StreetName, Block, City, PostalCode
            restaurant.street_name = parts[0]
            restaurant.street_block = parts[1]
            restaurant.city = parts[2]
            restaurant.postal_code = parts[3]
        elif len(parts) == 3:
            # Street name, Block/District, City
            restaurant.street_name = parts[0]
            restaurant.street_block = parts[1]
            restaurant.city = parts[2]
        elif len(parts) == 2:
            # City and postal code or block and city
            restaurant.city = parts[0]
            restaurant.postal_code = parts[1]
        elif len(parts) == 1:
            # Just city
            restaurant.city = parts[0]
        
        restaurant.save()


def reverse_migration(apps, schema_editor):
    """Reverse: clear component fields"""
    Restaurant = apps.get_model('restaurants', 'Restaurant')
    Restaurant.objects.all().update(
        city=None,
        street_block=None,
        street_name=None,
        street_number=None,
        postal_code=None
    )


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0003_restaurant_city_restaurant_postal_code_and_more'),
    ]

    operations = [
        migrations.RunPython(parse_and_populate_addresses, reverse_migration),
    ]