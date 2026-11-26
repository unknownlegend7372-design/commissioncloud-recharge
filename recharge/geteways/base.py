from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any


class PaymentGatewayAdapter(ABC):
    name: str = "base"

    @abstractmethod
    def build_payment_url(
        self,
        local_order_id: str,
        user_id: str,
        amount: Decimal,
        number: str,
        operator: str,
        callback_url: str,
    ) -> str:
        """पेमेंट गेटवे का रीडायरेक्ट/चेकआउट URL तैयार करें।"""

    @abstractmethod
    def verify_payment(
        self,
        local_order_id: str,
        gateway_order_id: str,
        fallback_utr: str = "",
        expected_amount: Decimal = Decimal("0.00"),
    ) -> Dict[str, Any]:
        """
        रिटर्न करता है:
        {
            "verified": bool,
            "status": str,
            "paid_amount": Decimal,
            "utr": str,
            "raw": dict,
        }
        """
