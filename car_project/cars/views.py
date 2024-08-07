import logging

from django.contrib.auth import login
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from cars.mixins import AuthMixin
from cars.models import Car
from cars.serializers import CarSerializer, UserRegistrationSerializer, UserLoginSerializer

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView,AuthMixin):
    """
    API view to register a new user.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle user registration and login.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            logger.info(f'User registered and logged in: {user.username}')
            return Response({
                'user': serializer.data,
                'token': self.get_tokens_for_user(user)
            }, status=status.HTTP_201_CREATED)
        logger.warning(f'Registration failed: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView,AuthMixin):
    """
    API view to log in an existing user.
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle user login and return JWT tokens.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            logger.info(f'User logged in: {user.username}')
            return Response({
                'user': user.username,
                'token': self.get_tokens_for_user(user)
            }, status=status.HTTP_200_OK)
        logger.warning(f'Login failed: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CarViewSet(viewsets.ModelViewSet):
    """
    API viewset for viewing and editing car instances.
    """
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['brand', 'model', 'year', 'fuel_type', 'transmission', 'miliage', 'price']
    ordering_fields = '__all__'
    ordering = ['id']

    def create(self, request, *args, **kwargs):
        """
        Create a new car instance.
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            logger.info(f'Car created: {serializer.data}')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            logger.warning(f'Car creation failed: {e.detail}')
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update an existing car instance.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(f'Car updated: {serializer.data}')
            return Response(serializer.data)
        except ValidationError as e:
            logger.warning(f'Car update failed: {e.detail}')
            return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete an existing car instance.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            logger.info(f'Car deleted: {instance.id}')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except NotFound:
            logger.warning('Car not found for deletion.')
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
