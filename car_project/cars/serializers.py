import logging
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from cars.models import Car

logger = logging.getLogger(__name__)

User = get_user_model()

class CarSerializer(serializers.ModelSerializer):
    """
    Serializer for the Car model.
    
    Validates the year, price, and stock of a car.
    """
    
    class Meta:
        model = Car
        fields = '__all__'

    def validate_year(self, value):
        """
        Validate the year of the car.
        
        Ensure the year is not earlier than 1886.
        """
        if value < 1886:
            logger.warning(f'Validation error in CarSerializer: Year {value} is before 1886.')
            raise serializers.ValidationError('Year cannot be earlier than 1886.')
        return value

    def validate_price(self, value):
        """
        Validate the price of the car.
        
        Ensure the price is a positive number.
        """
        if value <= 0:
            logger.warning(f'Validation error in CarSerializer: Price {value} is not positive.')
            raise serializers.ValidationError('Price must be a positive number.')
        return value
    
    def validate_stock(self, value):
        """
        Validate the stock of the car.
        
        Ensure the stock is not negative.
        """
        if value < 0:
            logger.warning(f'Validation error in CarSerializer: Stock {value} is negative.')
            raise serializers.ValidationError('Stock cannot be negative.')
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles user creation with validation for password strength.
    """
    
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        """
        Create a new user with the validated data.
        
        Logs the successful creation or any errors encountered.
        """
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password']
            )
            logger.info(f'User created successfully: {validated_data['username']}')
        except Exception as e:
            logger.error(f'Error creating user: {e}')
            raise
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Authenticates a user with provided credentials.
    """
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    user = serializers.SerializerMethodField()

    def validate(self, data):
        """
        Validate user credentials.
        
        Authenticate the user and log the success or failure.
        """
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            logger.warning(f'Invalid login attempt: Username {data['username']}.')
            raise serializers.ValidationError('Invalid credentials')
        logger.info(f'User authenticated successfully: {data['username']}')
        return {'user': user}

    def get_user(self, obj):
        """
        Retrieve the authenticated user.
        
        This method is used by the serializer to get the user object.
        """

        return obj.get('user', None)
