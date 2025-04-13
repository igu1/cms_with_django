from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from django.views.decorators.cache import never_cache
from django.conf import settings
import time
import os

@never_cache
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Checks:
    1. Database connection
    2. Static files
    3. Media files
    4. Environment variables
    """
    start_time = time.time()
    
    # Check database connection
    db_conn = True
    try:
        db_conn = connections['default'].cursor()
    except OperationalError:
        db_conn = False
    
    # Check static files directory
    static_files = os.path.exists(settings.STATIC_ROOT)
    
    # Check media files directory
    media_files = os.path.exists(settings.MEDIA_ROOT)
    
    # Check environment variables
    env_vars = {
        'DEBUG': settings.DEBUG,
        'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
        'DATABASE_URL': bool(os.getenv('DATABASE_URL')),
        'COMPANY_NAME': bool(settings.COMPANY_NAME),
    }
    
    # Overall status
    status = 'healthy' if db_conn and static_files and media_files else 'unhealthy'
    
    # Response time
    response_time = time.time() - start_time
    
    response = {
        'status': status,
        'response_time': f"{response_time:.4f}s",
        'database': 'connected' if db_conn else 'disconnected',
        'static_files': 'available' if static_files else 'unavailable',
        'media_files': 'available' if media_files else 'unavailable',
        'environment': env_vars,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    status_code = 200 if status == 'healthy' else 503
    
    return JsonResponse(response, status=status_code)
