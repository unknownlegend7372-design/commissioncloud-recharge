import os
from .base import PaymentGatewayAdapter
from .upi_gateway import UpiGatewayAdapter
from .jiopay import JioPayGatewayAdapter


def get_payment_gateway(gateway_name: str = "") -> PaymentGatewayAdapter:
    selected = (gateway_name or os.getenv("PAYMENT_GATEWAY", "upi_gateway")).strip().lower()
    if selected in ("jiopay", "jio_pay", "jio"):
        return JioPayGatewayAdapter()
    return UpiGatewayAdapter()
