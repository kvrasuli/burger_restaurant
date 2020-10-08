from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
