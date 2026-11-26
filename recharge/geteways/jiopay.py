import os
import urllib.parse
from decimal import Decimal
from typing import Dict, Any

from wallet import q_money
from .base import PaymentGatewayAdapter


class JioPayGatewayAdapter(PaymentGatewayAdapter):
    """
    JioPay Gateway Adapter — भविष्य में JioPay की API/URL/क्रेडेंशियल्स आने पर
    सिर्फ़ इसी फ़ाइल में बदलाव करना होगा।
    """

    name = "jiopay"

    def __init__(self):
        self.checkout_url = os.getenv("JIOPAY_CHECKOUT_URL", "").strip().rstrip("/")
        self.merchant_id = os.getenv("JIOPAY_MERCHANT_ID", "").strip()
        self.api_key = os.getenv("JIOPAY_API_KEY", "").strip()

    def build_payment_url(
        self,
        local_order_id: str,
        user_id: str,
        amount: Decimal,
        number: str,
        operator: str,
        callback_url: str,
    ) -> str:
        if not self.checkout_url:
            raise RuntimeError("JIOPAY_CHECKOUT_URL सेट नहीं है।")
        params = urllib.parse.urlencode({
            "merchant_id": self.merchant_id,
            "order_id": local_order_id,
            "amount": f"{q_money(amount):.2f}",
            "mobile": number,
            "operator": operator,
            "user_id": user_id,
            "redirect_url": callback_url,
        })
        return f"{self.checkout_url}?{params}"

    def verify_payment(
        self,
        local_order_id: str,
        gateway_order_id: str,
        fallback_utr: str = "",
        expected_amount: Decimal = Decimal("0.00"),
    ) -> Dict[str, Any]:
        # जब JioPay का status/verification endpoint मिले, तब यहाँ API call जोड़ें
        raise NotImplementedError("JioPay verify_payment अभी कॉन्फ़िगर नहीं किया गया है।")
