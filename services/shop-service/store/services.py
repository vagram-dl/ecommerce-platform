
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from .models import Wallet,Payment


class PaymentService:
    @classmethod
    def process_transaction(cls, user, amount, payment_type, idempotency_key):
        if amount <= 0:
            raise ValidationError("Сумма операции должна быть больше нуля")

        existing_payment = Payment.objects.filter(idempotency_key=idempotency_key).first()
        if existing_payment:
            return existing_payment

        try:
            with transaction.atomic():
                wallet, created = Wallet.objects.select_for_update().get_or_create(user=user)

                if payment_type == Payment.Type.WITHDRAWAL:
                    if wallet.balance < amount:
                        raise ValidationError("Недостаточно средств на балансе")
                    wallet.balance -= amount
                elif payment_type == Payment.Type.DEPOSIT:
                    wallet.balance += amount

                wallet.save()

                payment = Payment.objects.create(
                    user=user, amount=amount, type=payment_type,
                    idempotency_key=idempotency_key, status=Payment.Status.SUCCESS
                )

                return payment

        except ValidationError:
            Payment.objects.create(
                user=user, amount=amount, type=payment_type,
                idempotency_key=idempotency_key, status=Payment.Status.FAILED
            )
            raise
        except IntegrityError:
            return Payment.objects.get(idempotency_key=idempotency_key)



