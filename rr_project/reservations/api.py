
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404

from .models import *
from django.http import JsonResponse

@login_required
def api_get_reservation(request, reservation_id):
    if request.method == 'GET':
        try:
            reservation = get_object_or_404(Reservation, id=reservation_id)
            return JsonResponse({
                'success': True,
                'message': 'Reservation fetched successfully',
                'data': reservation.to_dict(),
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Something went wrong {e}'
            }, status=400)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Only GET allowed'
        }, status=404)