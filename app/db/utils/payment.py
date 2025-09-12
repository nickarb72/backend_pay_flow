from _decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
import hashlib
import hmac
import logging

from app.db.models import Account, Payment, User
from app.schemas.payment import WebhookResponse

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for processing payment webhooks from external systems."""

    @staticmethod
    def verify_signature(payload: dict, received_signature: str, secret_key: str) -> bool:
        """
        Verify webhook signature using HMAC-SHA256.

        Args:
            payload: Webhook payload data
            received_signature: Signature received from webhook
            secret_key: Secret key for signature generation

        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            signature_data = ''.join([
                str(payload['account_id']),
                str(payload['amount']),
                str(payload['transaction_id']),
                str(payload['user_id']),
                secret_key
            ])

            expected_signature = hashlib.sha256(signature_data.encode()).hexdigest()

            return hmac.compare_digest(expected_signature, received_signature)

        except KeyError as e:
            logger.error(f"Missing required field in payload: {e}")
            return False
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False

    @staticmethod
    async def process_webhook(
            db: AsyncSession,
            payload: dict,
            secret_key: str
    ) -> WebhookResponse:
        """
        Process incoming payment webhook.

        Args:
            db: Database session
            payload: Webhook payload data
            secret_key: Secret key for signature verification

        Returns:
            WebhookResponse: Processing result with details

        Raises:
            ValueError: If signature verification fails or data is invalid
        """
        if not WebhookService.verify_signature(payload, payload['signature'], secret_key):
            raise ValueError("Invalid signature")

        existing_payment = await db.get(Payment, payload['transaction_id'])
        if existing_payment:
            return WebhookResponse(
                transaction_id=payload['transaction_id'],
                user_id=existing_payment.user_id,
                account_id=existing_payment.account_id,
                amount=existing_payment.amount,
                created_at=existing_payment.created_at,
                message="Transaction already processed"
            )

        account = await db.get(Account, payload['account_id'])
        if not account:
            user = await db.get(User, payload['user_id'])
            if not user:
                raise ValueError(f"User with ID {payload['user_id']} not found")

            account = Account(
                id=payload['account_id'],
                user_id=payload['user_id'],
            )
            db.add(account)
            logger.info(f"Created new account {account.id} for user {user.id}")

        payment = Payment(
            transaction_id=payload['transaction_id'],
            user_id=payload['user_id'],
            account_id=payload['account_id'],
            amount=payload['amount'],
        )
        db.add(payment)

        amount = Decimal(str(payload['amount'])).quantize(Decimal('0.01'))
        await db.execute(
            update(Account)
            .where(Account.id == payload['account_id'])
            .values(balance=Account.balance + amount)
        )

        await db.refresh(payment)

        logger.info(f"Processed payment {payload['transaction_id']} for account {account.id}")

        return WebhookResponse(
            transaction_id=payload['transaction_id'],
            user_id=payload['user_id'],
            account_id=payload['account_id'],
            amount=payload['amount'],
            created_at=payment.created_at,
            message="Payment processed successfully"
        )
