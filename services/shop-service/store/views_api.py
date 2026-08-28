from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics,viewsets
from rest_framework.decorators import permission_classes

from .models import Product, Category, Wallet
from .serializers import ProductSerializer,CategorySerializer
from rest_framework.permissions import IsAdminUser,AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .serializers import PaymentSerializer
from .services import PaymentService
from .models import Wallet, Payment
from django.core.exceptions import ValidationError as DjangoValidationError


class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                payment = PaymentService.process_transaction(
                    user = request.user,
                    amount=serializer.validated_data['amount'],
                    payment_type=serializer.validated_data['type'],
                    idempotency_key=serializer.validated_data['idempotency_key']
                )

                return Response({
                    "message" : "Операция выполнена",
                    "payment_status" : payment.status,
                    "current_balance" : request.user.wallet.balance

                }, status = status.HTTP_201_CREATED)
            except DjangoValidationError as e:
                return Response({
                    "error" : str(e)
                }, status = status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list','retrieve']:
            permission_classes= [AllowAny]
        elif self.action in ['create','update','partial_update','destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category__slug']

    def get_permissions(self):
        if self.action in ['list','retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['create']:
            permission_classes = [IsAdminUser]
        elif self.action in ['update','partial_update']:
            permission_classes = [IsAdminUser]
        elif self.action in ['destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class WalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)

        return Response({
            "balance" : wallet.balance,
            "currency" : "RUB"
        }, status=status.HTTP_200_OK)

class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')

        payments_data = []
        for payment in payments:
                payments_data.append({
                    "id": payment.id,
                    "amount": str(payment.amount),
                    "type": payment.type,
                    "status": payment.status,
                    "created_at": payment.created_at.isoformat()
                })
        return Response({
            "total_count": len(payments_data),
            "payments": payments_data
        },status=status.HTTP_200_OK)