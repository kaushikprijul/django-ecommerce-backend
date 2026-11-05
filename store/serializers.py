from rest_framework import serializers

from .models import (
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem
)


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ['cart']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than zero."
            )
        return value


class CartSerializer(serializers.ModelSerializer):

    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'created_at',
            'items'
        ]
        read_only_fields = ['user', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'quantity',
            'price'
        ]
        read_only_fields = ['price']


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'total_amount',
            'created_at',
            'status',
            'items'
        ]

        read_only_fields = [
            'user',
            'total_amount',
            'created_at',
            'status'
        ]