from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any


class RechargeProviderAdapter(ABC):
    name: str = "base"

    @abstractmethod
    def resolve_operator_code(self, operator_name: str, plan_hint: str = "") -> str:
        """ऑपरेटर नाम से प्रोवाइडर का ऑपरेटर/B2B कोड निकालें।"""

    @abstractmethod
    def execute_recharge(
        self,
        local_order_id: str,
        operator: str,
        number: str,
        amount: Decimal,
        plan_hint: str = "",
    ) -> Dict[str, Any]:
        """
        रिटर्न करता है:
        {
            "final_status": "RECHARGE_SUCCESS" | "RECHARGE_PENDING" | "RECHARGE_FAILED",
            "txid": str,
            "opid": str,
            "raw_msg": str,
        }
        """

    @abstractmethod
    def check_status(self, order_id: str, fallback_txid: str = "") -> Dict[str, Any]:
        """
        रिटर्न करता है:
        {
            "mapped_status": "SUCCESS" | "FAILED" | "PENDING",
            "txid": str,
            "opid": str,
        }
        """
