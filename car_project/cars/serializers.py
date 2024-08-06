from rest_framework import serializers

from cars.models import Car


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

    def validate_year(self, value):
        if value < 1886:
            raise serializers.ValidationError("Год выпуска не может быть раньше 1886.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть положительным числом.")
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Количество на складе не может быть отрицательным.")
        return value
