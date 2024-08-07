from django.contrib import admin

# Register your models here.



from django.shortcuts import redirect
from django.urls import reverse

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        public_routes = [reverse('login'), reverse('register')]
        if not request.user.is_authenticated and request.path not in public_routes:
            return redirect(reverse('login'))
        response = self.get_response(request)
        return response