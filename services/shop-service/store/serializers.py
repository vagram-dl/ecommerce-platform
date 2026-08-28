import uuid
from decimal import Decimal
from rest_framework import serializers
from .models import Product
from .models import Category
from .models import Payment

class PaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )

    type = serializers.ChoiceField(
        choices=Payment.Type.choices
    )

    idempotency_key = serializers.UUIDField(
        default=uuid.uuid4
    )

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','slug','description']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','description','price','category']