
from django.shortcuts import get_object_or_404
from accounts.models import Owner
from restaurants.models import Table, Element, Restaurant, Floorplan
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json

@require_http_methods(["POST"])
@csrf_exempt
def api_save_floor_plan(request):
    """API endpoint for saving floor plan (tables, elements & dimensions)"""
    try:
        owner = get_object_or_404(Owner, user=request.user)
        data = json.loads(request.body)
        
        restaurant_id = data.get('restaurant_id')
        tables_data = data.get('tables', [])
        elements_data = data.get('elements', [])
        floorplan_data = data.get('floorplan', {})
        
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=owner)
        
        with transaction.atomic():
            floorplan = None
            if floorplan_data:
                floorplan_obj = Floorplan.objects.filter(restaurant=restaurant).first()
                if floorplan_obj:
                    floorplan_obj.width = floorplan_data.get('width', floorplan_obj.width)
                    floorplan_obj.height = floorplan_data.get('height', floorplan_obj.height)
                    floorplan_obj.save()
                    floorplan = floorplan_obj
                else:
                    floorplan = Floorplan.objects.create(
                        restaurant=restaurant,
                        width=floorplan_data.get('width', 1000),
                        height=floorplan_data.get('height', 600)
                    )
            else:
                floorplan = Floorplan.objects.filter(restaurant=restaurant).first()
                if not floorplan:
                    floorplan = Floorplan.objects.create(
                        restaurant=restaurant,
                        width=1000,
                        height=600
                    )
            
            # Save tables
            table_ids = []
            for table in tables_data:
                if table.get('new'):
                    t = Table.objects.create(
                        floorplan=floorplan,
                        number=table['number'],
                        capacity=table['capacity'],
                        x=table['x'],
                        y=table['y'],
                    )
                    table_ids.append(t.id)
                else:
                    t, _ = Table.objects.update_or_create(
                        id=table.get('id'),
                        defaults={
                            'floorplan': floorplan,
                            'number': table['number'],
                            'capacity': table['capacity'],
                            'x': table['x'],
                            'y': table['y'],
                        }
                    )
                    table_ids.append(t.id)
            
            # Save elements
            element_ids = []
            for element in elements_data:
                if element.get('new'):
                    e = Element.objects.create(
                        floorplan=floorplan,
                        name=element['name'],
                        x=element['x'],
                        y=element['y'],
                        height=element['height'],
                        width=element['width']
                    )
                    element_ids.append(e.id)
                else:
                    e, _ = Element.objects.update_or_create(
                        id=element.get('id'),
                        defaults={
                            'floorplan': floorplan,
                            'name': element['name'],
                            'x': element['x'],
                            'y': element['y'],
                            'height': element['height'],
                            'width': element['width']
                        }
                    )
                    element_ids.append(e.id)
            
            # Delete removed tables/elements
            Table.objects.filter(floorplan=floorplan).exclude(id__in=table_ids).delete()
            Element.objects.filter(floorplan=floorplan).exclude(id__in=element_ids).delete()
        
        return JsonResponse({'success': True, 'message': 'Floor plan saved successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
