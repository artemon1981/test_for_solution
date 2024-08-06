from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cars.views import CarViewSet,RegisterView,LoginView

router = DefaultRouter()
router.register(r'cars', CarViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]
