import os
import re
import logging
from django.conf import settings
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware to display a maintenance page when MAINTENANCE_MODE is enabled.

    To enable maintenance mode, set MAINTENANCE_MODE=True in your .env file
    or as an environment variable.
    """

    def process_request(self, request):
        # Check if maintenance mode is enabled
        maintenance_mode = os.getenv('MAINTENANCE_MODE', 'False') == 'True'

        # Skip maintenance mode for certain IPs
        if maintenance_mode:
            # Allow access to static files
            if request.path.startswith('/static/') or request.path.startswith('/media/'):
                return None

            # Allow access to the admin site
            if request.path.startswith('/admin/'):
                return None

            # Allow access to health check endpoint
            if request.path == '/health/':
                return None

            # Check for allowed IPs
            allowed_ips = os.getenv('MAINTENANCE_ALLOWED_IPS', '').split(',')
            client_ip = self._get_client_ip(request)

            if client_ip and client_ip in allowed_ips:
                return None

            # Show maintenance page
            context = {
                'COMPANY_NAME': settings.COMPANY_NAME,
            }
            return render(request, 'maintenance.html', context, status=503)

        return None

    def _get_client_ip(self, request):
        """Get the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DebugStaticFilesMiddleware(MiddlewareMixin):
    """
    Middleware to debug static file serving issues.
    """

    def process_request(self, request):
        if request.path.startswith('/static/'):
            logger.info(f"Static file requested: {request.path}")
            logger.info(f"STATIC_URL: {settings.STATIC_URL}")
            logger.info(f"STATIC_ROOT: {settings.STATIC_ROOT}")
            logger.info(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
            logger.info(f"STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """

    def process_response(self, request, response):
        # Only add security headers if not already present and not for static/media files
        if not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            # Content Security Policy
            if not response.has_header('Content-Security-Policy'):
                csp = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.tailwindcss.com; "
                    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                    "img-src 'self' data:; "
                    "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
                    "connect-src 'self'; "
                    "frame-ancestors 'none'; "
                    "form-action 'self';"
                )
                response['Content-Security-Policy'] = csp

            # X-Content-Type-Options
            if not response.has_header('X-Content-Type-Options'):
                response['X-Content-Type-Options'] = 'nosniff'

            # X-Frame-Options
            if not response.has_header('X-Frame-Options'):
                response['X-Frame-Options'] = 'DENY'

            # X-XSS-Protection
            if not response.has_header('X-XSS-Protection'):
                response['X-XSS-Protection'] = '1; mode=block'

            # Referrer-Policy
            if not response.has_header('Referrer-Policy'):
                response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

            # Permissions-Policy
            if not response.has_header('Permissions-Policy'):
                response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

            # HSTS (only in production)
            if not settings.DEBUG and not response.has_header('Strict-Transport-Security'):
                response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        return response
