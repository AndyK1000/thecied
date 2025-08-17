from django.shortcuts import redirect
from django.urls import reverse


class SubdomainRoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is admin subdomain
        host = request.get_host()
        
        if host.startswith('admin.') or 'admin.' in host:
            # If accessing admin subdomain but not admin dashboard URLs
            if not request.path.startswith('/admin_dashboard/'):
                return redirect('/admin_dashboard/')
        
        response = self.get_response(request)
        return response
