import uuid
from unittest import skipIf

from django.conf import settings
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APITestCase,APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from store.models import Wallet, Payment
from store.services import PaymentService
import threading
from django.test import TransactionTestCase
from django.conf import settings
from unittest import skipIf

class PaymentServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser',password='testpass123')
        self.wallet = Wallet.objects.create(user=self.user, balance=1000)
        self.idempotency_key = uuid.uuid4()

    def test_deposit_increases_balance(self):
        payment = PaymentService.process_transaction(
            user=self.user, amount=500, payment_type=Payment.Type.DEPOSIT,
            idempotency_key=self.idempotency_key
        )

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 1500)
        self.assertEqual(payment.status, Payment.Status.SUCCESS)
        self.assertEqual(payment.type, Payment.Type.DEPOSIT)

    def test_withdrawal_decreases_balance(self):
        payment = PaymentService.process_transaction(
            user=self.user, amount=300, payment_type=Payment.Type.WITHDRAWAL,
            idempotency_key=self.idempotency_key
        )

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 700)
        self.assertEqual(payment.status, Payment.Status.SUCCESS)

    def test_withdrawal_insufficient_funds(self):
        with self.assertRaises(ValidationError) as context:
            PaymentService.process_transaction(
                user=self.user, amount=2000.00, payment_type=Payment.Type.WITHDRAWAL,
                idempotency_key=self.idempotency_key
            )

        self.assertIn("Недостаточно средств", str(context.exception))

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 1000)

        failed_payment = Payment.objects.filter(idempotency_key=self.idempotency_key).first()
        self.assertIsNotNone(failed_payment)
        self.assertEqual(failed_payment.status, Payment.Status.FAILED)

    def test_idempotency_prevents_double_charge(self):
        key = uuid.uuid4()

        payment1 = PaymentService.process_transaction(
            user=self.user, amount=500, payment_type=Payment.Type.DEPOSIT,
            idempotency_key=key
        )

        payment2 = PaymentService.process_transaction(
            user=self.user, amount=500, payment_type=Payment.Type.DEPOSIT,
            idempotency_key=key
        )

        self.assertEqual(payment1.id, payment2.id)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, 1500)

class PaymentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser',password='apipass123')
        self.wallet = Wallet.objects.create(user=self.user,balance=5000)

        self.refresh = RefreshToken.for_user(self.user)
        self.client=APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')

        self.payment_url = reverse('payment-api')
        self.balance_url = reverse('wallet-balance')
        self.history_url = reverse('payment-history')

    def test_api_deposit_success(self):
        data = {
            "amount" : "1000",
            "type" : "deposit"
        }
        response = self.client.post(self.payment_url, data,format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Операция выполнена")
        self.assertEqual(response.data['payment_status'], "success")
        self.assertEqual(float(response.data['current_balance']), 6000)

    def test_api_withdrawal_insufficient_funds(self):
        data = {
            "amount" : 99999,
            "type" : "withdraw",
            "idempotency_key": str(uuid.uuid4())
        }
        response = self.client.post(self.payment_url,data,format='json')


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Недостаточно средств", response.data['error'])

    def test_api_get_balance(self):
        response = self.client.get(self.balance_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['balance']), 5000.00)
        self.assertEqual(response.data['currency'], "RUB")

    def test_api_get_history(self):
        Payment.objects.create(
            user=self.user, amount=500, type=Payment.Type.DEPOSIT,
            idempotency_key = uuid.uuid4(), status = Payment.Status.SUCCESS
        )

        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_count'],1)
        self.assertEqual(float(response.data['payments'][0]['amount']),500.00)

    def test_api_unauthorized_access(self):
        self.client.credentials()

        response = self.client.get(self.balance_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_idempotency_prevents_duplicate_payment(self):
        key = str(uuid.uuid4())

        data = {
            "amount" : 1000,
            "type" : "deposit",
            "idempotency_key" : key
        }

        response1 = self.client.post(self.payment_url,data,format='json')
        response2 = self.client.post(self.payment_url,data,format='json')

        self.assertEqual(response1.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.wallet.refresh_from_db()
        self.assertEqual(float(self.wallet.balance),6000.00)

@skipIf(
    settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3',
    "SQLite doesn't support proper row-level locking for concurrency tests"
)
class PaymentConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='concurrency_user', password= 'testpass123')
        self.wallet = Wallet.objects.create(user=self.user, balance=1000)

    def test_concurrent_withdrawals(self):
            results = []
            barrier = threading.Barrier(2)

            def try_withdraw(amount,key):
                barrier.wait()
                try:
                    PaymentService.process_transaction(
                        user=self.user, amount=amount,payment_type=Payment.Type.WITHDRAWAL,
                        idempotency_key=key
                    )
                    results.append('success')
                except ValidationError:
                    results.append('failed')

            t1 = threading.Thread(target=try_withdraw,args=(600, uuid.uuid4()))
            t2 = threading.Thread(target=try_withdraw,args=(600,uuid.uuid4()))

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            self.wallet.refresh_from_db()

            self.assertEqual(self.wallet.balance, 400)
            self.assertEqual(results.count('success'),1)
            self.assertEqual(results.count('failed'),1)