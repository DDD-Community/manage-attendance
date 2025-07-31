from django.http import JsonResponse
import datetime

def health_check(request):
    response_data = {
        'code': 200,
        'message': 'healthy',
        'data': {
            'status': 'healthy',
            'timestamp': datetime.datetime.now(datetime.timezone.utc)
                .isoformat()
                .replace('+00:00', 'Z')
        }
    }
    return JsonResponse(response_data)
