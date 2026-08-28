from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import ProductViewSet, CategoryViewSet, PaymentAPIView, WalletBalanceView, PaymentHistoryView

router = DefaultRouter()
router.register(r'products',ProductViewSet,basename = 'product')
router.register(r'categories',CategoryViewSet,basename = 'category')

urlpatterns = [
    path('', include(router.urls)),
    path('payments/', PaymentAPIView.as_view(), name='payment-api'),
    path('wallet/balance/', WalletBalanceView.as_view(), name='wallet-balance'),
    path('payments/history/', PaymentHistoryView.as_view(),name='payment-history'),
]