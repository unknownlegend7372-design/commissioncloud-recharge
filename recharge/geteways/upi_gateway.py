import os
import urllib.parse
from decimal import Decimal
from typing import Dict, Any
import requests

try:
    from wallet import q_money
except ImportError:
    from ..wallet import q_money

from .base import PaymentGatewayAdapter


class UpiGatewayAdapter(PaymentGatewayAdapter):
    name = "upi_gateway"

    def __init__(self, base_url: str = "", timeout: int = 10):
        self.base_url = (
            base_url
            or os.getenv("PAYMENT_GATEWAY_URL", "https://upi-geteway-s19b.onrender.com")
        ).strip().rstrip("/")
        self.timeout = timeout

    def build_payment_url(
        self,
        local_order_id: str,
        user_id: str,
        amount: Decimal,
        number: str,
        operator: str,
        callback_url: str,
        upi_app: str = "",
    ) -> str:
        query = {
            "amount": f"{q_money(amount):.2f}",
            "mobile": number,
            "operator": operator,
            "user_id": user_id,
            "order_id": local_order_id,
            "redirect_url": callback_url,
        }
        if upi_app:
            query["upi_app"] = upi_app.strip().lower()
        params = urllib.parse.urlencode(query)
        return f"{self.base_url}/?{params}"

    def verify_payment(
        self,
        local_order_id: str,
        gateway_order_id: str,
        fallback_utr: str = "",
        expected_amount: Decimal = Decimal("0.00"),
    ) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/api/payment/status/{gateway_order_id}",
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json() if resp.content else {}

        gw_status = str(data.get("status", "")).upper()
        paid_amt = q_money(data.get("amount", 0))
        utr = str(
            fallback_utr or data.get("utr", "") or data.get("txnid", "")
        ).replace("#", "").strip().upper()

        is_paid = ("PAID" in gw_status) and (
            abs(paid_amt - q_money(expected_amount)) <= Decimal("0.05")
        )
        return {
            "verified": is_paid,
            "status": gw_status,
            "paid_amount": paid_amt,
            "utr": utr,
            "raw": data,
        }
