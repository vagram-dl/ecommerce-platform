from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views_api import CategoryViewSet, PaymentAPIView, PaymentHistoryView, ProductViewSet, WalletBalanceView

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
    path("payments/", PaymentAPIView.as_view(), name="payment-api"),
    path("wallet/balance/", WalletBalanceView.as_view(), name="wallet-balance"),
    path("payments/history/", PaymentHistoryView.as_view(), name="payment-history"),
    path("test-auth/", views.test_auth, name="test_auth"),
]
