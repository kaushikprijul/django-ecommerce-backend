from decimal import Decimal

from django.db import transaction
from django.db.models import F

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Product, Cart, CartItem, Order, OrderItem

from .serializers import (
    ProductSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer
)

from .permissions import ProductPermission


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [ProductPermission]

    filterset_fields = {
        'price': ['gte', 'lte'],
    }

    search_fields = ['name', 'description']

    ordering_fields = ['price', 'created_at']

    ordering = ['-created_at']


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
        )

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        if product.stock < quantity:
            raise ValidationError(
                "Insufficient product stock."
            )

        cart = Cart.objects.filter(
            user=request.user
        ).order_by('id').first()

        if cart is None:
            cart = Cart.objects.create(user=request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            new_quantity = item.quantity + quantity

            if new_quantity > product.stock:
                raise ValidationError(
                    "Requested quantity exceeds available stock."
                )

            item.quantity = new_quantity
            item.save()

        return Response(
            CartItemSerializer(item).data,
            status=status.HTTP_201_CREATED
        )

    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data.get(
            'product', instance.product
        )
        quantity = serializer.validated_data.get(
            'quantity', instance.quantity
        )

        if quantity <= 0:
            raise ValidationError(
                "Quantity must be greater than zero."
            )

        if quantity > product.stock:
            raise ValidationError(
                "Requested quantity exceeds available stock."
            )

        serializer.save()

        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items')

    def create(self, request, *args, **kwargs):

        cart = Cart.objects.filter(
            user=request.user
        ).first()

        if not cart:
            raise ValidationError(
                "Cart not found."
            )

        with transaction.atomic():

            cart_items = list(
                cart.items.select_related('product')
            )

            if not cart_items:
                raise ValidationError(
                    "Your cart is empty."
                )

            total = Decimal('0.00')
            locked_products = {}

            for item in cart_items:

                product = Product.objects.select_for_update().get(
                    pk=item.product_id
                )

                if product.stock < item.quantity:
                    raise ValidationError(
                        f"Insufficient stock for {product.name}."
                    )

                locked_products[product.id] = product

            order = Order.objects.create(
                user=request.user,
                total_amount=Decimal('0.00')
            )

            for item in cart_items:

                product = locked_products[item.product_id]

                price = product.price
                subtotal = price * item.quantity

                total += subtotal

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=price
                )

                product.stock = F('stock') - item.quantity

                product.save(
                    update_fields=['stock']
                )

            order.total_amount = total

            order.save(
                update_fields=['total_amount']
            )

            cart.items.all().delete()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )