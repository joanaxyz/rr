import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rr_project.settings')
django.setup()

from restaurants.models import Restaurant, Floorplan, Table, Element

def populate_restaurant_floor_plan(restaurant):
    """Create a realistic 800x600 floor plan for a restaurant"""
    
    floorplan, created = Floorplan.objects.get_or_create(
        restaurant=restaurant,
        defaults={'width': 800, 'height': 600}
    )
    
    if not created:
        floorplan.width = 800
        floorplan.height = 600
        floorplan.save()
    
    Table.objects.filter(floorplan=floorplan).delete()
    Element.objects.filter(floorplan=floorplan).delete()
    
    elements_data = [
        {'name': 'Kitchen', 'x': 10, 'y': 10, 'width': 150, 'height': 120},
        {'name': 'Bar', 'x': 620, 'y': 10, 'width': 170, 'height': 80},
        {'name': 'Entrance', 'x': 10, 'y': 540, 'width': 100, 'height': 50},
        {'name': 'Restrooms', 'x': 690, 'y': 540, 'width': 100, 'height': 50},
    ]
    
    for elem in elements_data:
        Element.objects.create(
            floorplan=floorplan,
            name=elem['name'],
            x=elem['x'],
            y=elem['y'],
            width=elem['width'],
            height=elem['height']
        )
    
    tables_data = [
        (2, 180, 150), (2, 280, 150), (2, 380, 150), (2, 480, 150),
        (4, 180, 260), (4, 280, 260), (4, 380, 260), (4, 480, 260),
        (4, 180, 370), (4, 280, 370), (4, 380, 370), (4, 480, 370),
        (6, 230, 470), (6, 380, 470),
        (2, 580, 180), (2, 680, 180),
        (4, 580, 320), (4, 680, 320),
    ]
    
    table_num = 1
    for capacity, x, y in tables_data:
        Table.objects.create(
            floorplan=floorplan,
            number=table_num,
            capacity=capacity,
            x=x,
            y=y,
            status='available'
        )
        table_num += 1
    
    print(f"[OK] {restaurant.name}: {len(tables_data)} tables, {len(elements_data)} elements")

restaurants = Restaurant.objects.all()
print(f"Populating {restaurants.count()} restaurants with floor plans:\n")
for r in restaurants:
    populate_restaurant_floor_plan(r)
print("\nDone!")
