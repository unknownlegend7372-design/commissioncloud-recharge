import logging
import os
from decimal import Decimal
from typing import Dict, Any
import requests

from .base import RechargeProviderAdapter

logger = logging.getLogger("commissioncloud.provider.a1topup")

A1_OPERATOR_CODES = {
    "Airtel": "A",
    "BSNL - STV": "BR",
    "BSNL Combo": "BR",
    "BSNL_STV": "BR",
    "BSNL": "BR",
    "BSNL - TOPUP": "BT",
    "BSNL Topup": "BT",
    "Idea": "I",
    "RELIANCE - JIO": "RC",
    "Jio": "RC",
    "Vodafone": "V",
    "Vi": "V",
    "Airtel Digital DTH TV": "ATV",
    "Airtel DTH": "ATV",
    "DISH TV": "DTV",
    "Dish TV": "DTV",
    "SUNDIRECT DTH TV": "STV",
    "Sun Direct": "STV",
    "TATASKY DTH TV": "TTV",
    "Tata Play": "TTV",
    "VIDEOCON DTH TV": "VTV",
    "Videocon d2h": "VTV",
    "Adani power": "AEML",
    "Ajmer Vidyut Vitran Nigam - RAJASTHAN": "AJV",
    "APDCL (Non-RAPDR) - ASSAM": "APDCLN",
    "APEPDCL - ANDHRA PRADESH": "APEPDCL",
    "Assam Power Distribution Company Ltd (RAPDR)": "APDCLR",
    "Bangalore ElectricitySupply Company": "BESCOM",
    "BEST Mumbai": "BEST",
    "BharatpurElectricityServicesLtd": "BHES",
    "Bikaner Electricity Supply Limited": "BESL",
    "BrihanMumbaiElectricSupplyandTransportUndertaking": "BMESTU",
    "BSES Rajdhani Power Limited - Delhi": "BSES",
    "BSES Yamuna Power Limited - Delhi": "BSESY",
    "Central Power Distribution Company of Andhra Pradesh Ltd": "APCPDCL",
    "CESC - WEST BENGAL": "CESC",
    "Chamundeshwari Electricity Supply Corporation Ltd. (Cesc,Mysore)": "CESCOM",
    "Chhattisgarh State Power Distribution Company Ltd. (CSPDCL)": "CSPDCL",
    "Dakshin Gujarat Vij Company Ltd": "DGVCL",
    "DakshinHaryanaBijliVitranNigam": "DHBVN",
    "Department of Power Arunachal Pradesh": "ARPDOP",
    "Department of Power, Nagaland": "NDOP",
    "DNHPowerDistributionCompanyLimited": "DDCL",
    "Gift Power Company Limited": "GPCL",
    "Goa Electricity": "GOAELC",
    "Government of Puducherry Electricity Department": "PGPED",
    "GulbargaElectricitySupplyCompanyLimited": "GESCL",
    "Himachal Pradesh State Electricity Board Ltd": "HPSEBL",
    "Hubli Electricity Supply Company Ltd. (HESCOM)": "HESCOM",
    "India Power - WEST BENGAL": "IPWB",
    "IndiaPowerCorporationLimited": "IPCL",
    "Jaipur Vidyut Vitran Nigam - RAJASTHAN": "JVV",
    "Jammu & Kashmir power Development department": "JKPDD",
    "JamshedpurUtilitiesandServicesCompanyLimited": "JUSCL",
    "JBVNL - JHARKHAND": "JBVNL",
    "Jodhpur Vidyut Vitran Nigam - RAJASTHAN": "JDVV",
    "kannan devan hills power": "KDHPCPL",
    "Kanpur Electricity Supply Company": "KESCO",
    "KEDL - KOTA": "KEDL",
    "Kerala State Electricity Board Ltd.": "KSEB",
    "Lakshadweep Electricity Department": "LED",
    "Madhya Gujarat Vij Company Ltd": "MGVCL",
    "Madhya Pradesh Madhya Kshetra Vidyut Vitaran-RURAL": "MPPKVVCLMR",
    "Madhya Pradesh Poorv Kshetra Vidyut Vitaran-URBAN": "MPPKVVCL",
    "Madhyanchal Vidyut Vitran Nigam Limited": "MVVNL",
    "Mangalore Electricity Supply Co. Ltd (MESCOM) - RAPDR": "MESCOMR",
    "Mangalore Electricity Supply Co. Ltd (Non) - RAPDR": "MESCOMNR",
    "Manipur State Power Distribution Company Limited (Prepaid)": "MSPDCLPR",
    "MEPDCL - MEGHALAYA": "MEPDCL",
    "MP Madhaya Kshetra Vidyut Vitaran -Urban": "MKV",
    "MP Poorv Kshetra Vidyut Vitaran - Jabalpur": "MPPKVVCLPU",
    "MP Poorv Kshetra Vidyut Vitaran - Rular": "MPPKVVCLPU",
    "MSEDC - MAHARASHTRA": "MSEDC",
    "MUNICIPALCORPORATIONOFGURUGRAM": "MCG",
    "Muzaffarpur Vidyut Vitran": "MVV",
    "NESCO Odisha": "NESCO",
    "New Delhi Municipal Council (NDMC) - Electricity": "NDMC",
    "Noida Power - NOIDA": "NP",
    "North Bihar Electricity": "NBE",
    "NorthDelhiPowerLimited": "NDPL",
    "Paschim Gujarat Vij Company Ltd": "PGVCL",
    "Paschim Kshetra Vidyut Vitaran - MADHYA PRADESH": "PKV",
    "Power & Electricity Department - Mizoram": "MPED",
    "Punjab State Power Corporation Limted": "PSPCL",
    "Reliance Energy": "RELIANCE",
    "Sikkim Power Rural": "SPR",
    "Sikkim Power Urban": "SPU",
    "SNDL Power - NAGPUR": "SNDL",
    "South Bihar Electricity": "SBE",
    "SOUTHCO Odisha": "SOUTHCO",
    "Southern Power - ANDHRA PRADESH": "SPA",
    "Southern Power - TELANGANA": "SPT",
    "Tata Power - MUMBAI": "TPDM",
    "Tata Power Delhi Limited - Delhi": "TPD",
    "TNEB - TAMIL NADU": "TNEB",
    "Torrent Power agra": "TRP",
    "Torrent Power Ahemdabad": "TORRENTAHM",
    "Torrent Power Bhivandi": "TORRENTBHI",
    "Torrent Power Dahej": "TORRENTDAH",
    "Torrent Power SHIL": "TORRENTSHI",
    "Torrent Power Surat": "TORRENTSUR",
    "TP Ajmer Distribution Ltd": "TPADL",
    "TP central odisha distribution limited": "TPCODL",
    "TripuraStateElectricityCorporationLtd": "TSECL",
    "TSNPDCL Telangana northern power": "TSNPDCL",
    "UPPCL (URBAN) - UTTAR PRADESH": "UPPCLU",
    "Uttar Pradesh Power Corporation Limited(Rular)": "UPPCLR",
    "UttarakhandPowerCorporationLimited": "UKPCL",
    "UttarGujarat Vij Company Ltd": "UGVCL",
    "UttarHaryanaBijliVitranNigam": "UHBV",
    "WBSEDCL - WEST BENGAL": "WBSEDCL",
    "Western Electricity supply co. Of orissa ltd.": "WESCO",
    "Adani Gas": "AG",
    "Gujarat Gas": "GG",
    "Hindustan Petroleum Corporation Ltd": "HPCLGC",
    "Indraprastha Gas": "IG",
    "Mahanagar Gas": "MG",
    "Airtel Payments Bank": "APB",
    "Axis Bank Fastag": "AXF",
    "Bank Of Baroda - Fastag": "BBF",
    "Equitas Fastag Recharge": "EFF",
    "Federal Bank - Fastag": "FDF",
    "Hdfc Bank - Fastag": "HDF",
    "Icici Bank Fastag": "ICF",
    "Idbi Bank Fastag": "IBF",
    "Idfc First Bank- Fastag": "IFF",
    "Indian Highways Management Company Ltd Fastag": "IHMCF",
    "Indusind Bank Fastag": "INDF",
    "Jammu And Kashmir Bank Fastag": "JKF",
    "Kotak Mahindra Bank - Fastag": "KMF",
    "Paul Merchants": "PMF",
    "Paytm Payments Bank Fastag": "PTF",
    "Sbi Bank Fastag": "SBF",
}

MOBILE_OPERATORS = {
    "Airtel", "BSNL - STV", "BSNL Combo", "BSNL_STV", "BSNL",
    "BSNL - TOPUP", "BSNL Topup", "Idea", "RELIANCE - JIO", "Jio",
    "Vodafone", "Vi"
}

BILLER_LISTS_BY_TYPE = {
    "DTH": [
        "Airtel Digital DTH TV",
        "DISH TV",
        "SUNDIRECT DTH TV",
        "TATASKY DTH TV",
        "VIDEOCON DTH TV",
    ],
    "Electricity": [k for k in A1_OPERATOR_CODES.keys() if k not in {
        *MOBILE_OPERATORS,
        "Airtel Digital DTH TV", "Airtel DTH", "DISH TV",
        "Dish TV", "SUNDIRECT DTH TV", "Sun Direct", "TATASKY DTH TV",
        "Tata Play", "VIDEOCON DTH TV", "Videocon d2h",
        "Adani Gas", "Gujarat Gas", "Hindustan Petroleum Corporation Ltd",
        "Indraprastha Gas", "Mahanagar Gas",
        "Airtel Payments Bank", "Axis Bank Fastag", "Bank Of Baroda - Fastag",
        "Equitas Fastag Recharge", "Federal Bank - Fastag", "Hdfc Bank - Fastag",
        "Icici Bank Fastag", "Idbi Bank Fastag", "Idfc First Bank- Fastag",
        "Indian Highways Management Company Ltd Fastag", "Indusind Bank Fastag",
        "Jammu And Kashmir Bank Fastag", "Kotak Mahindra Bank - Fastag",
        "Paul Merchants", "Paytm Payments Bank Fastag", "Sbi Bank Fastag",
    }],
    "Gas": [
        "Adani Gas",
        "Gujarat Gas",
        "Hindustan Petroleum Corporation Ltd",
        "Indraprastha Gas",
        "Mahanagar Gas",
    ],
    "FASTag": [
        "Airtel Payments Bank",
        "Axis Bank Fastag",
        "Bank Of Baroda - Fastag",
        "Equitas Fastag Recharge",
        "Federal Bank - Fastag",
        "Hdfc Bank - Fastag",
        "Icici Bank Fastag",
        "Idbi Bank Fastag",
        "Idfc First Bank- Fastag",
        "Indian Highways Management Company Ltd Fastag",
        "Indusind Bank Fastag",
        "Jammu And Kashmir Bank Fastag",
        "Kotak Mahindra Bank - Fastag",
        "Paul Merchants",
        "Paytm Payments Bank Fastag",
        "Sbi Bank Fastag",
    ],
}

VALID_A1_CODES = {code.upper(): code for code in A1_OPERATOR_CODES.values()}


class A1TopupProvider(RechargeProviderAdapter):
    name = "a1topup"

    def __init__(self):
        self.api_token = os.getenv("A1TOPUP_TOKEN", "").strip()
        self.mode = os.getenv("A1TOPUP_MODE", "sandbox").strip().lower()
        self.base_url = (
            "https://business.a1topup.com/recharge/api"
            if self.mode == "live"
            else "https://business.a1topup.com/sandbox/api"
        )
        self.status_url = (
            "https://business.a1topup.com/recharge/status"
            if self.mode == "live"
            else "https://business.a1topup.com/sandbox/status"
        )

    def resolve_operator_code(self, operator_name: str, plan_hint: str = "") -> str:
        op_clean = (operator_name or "").replace("#", "").strip()
        op_lower = op_clean.lower()
        hint_lower = (plan_hint or "").replace("#", "").strip().lower()

        if not op_clean:
            return ""
        if op_clean.upper() in VALID_A1_CODES:
            return VALID_A1_CODES[op_clean.upper()]
        if "bsnl" in op_lower:
            if "topup" in op_lower or "top-up" in op_lower or "topup" in hint_lower or "talktime" in hint_lower:
                return "BT"
            return "BR"
        if op_clean in A1_OPERATOR_CODES:
            return A1_OPERATOR_CODES[op_clean]
        for key, code in A1_OPERATOR_CODES.items():
            if key.lower() == op_lower:
                return code
        return op_clean

    def execute_recharge(
        self,
        local_order_id: str,
        operator: str,
        number: str,
        amount: Decimal,
        plan_hint: str = "",
    ) -> Dict[str, Any]:
        if not self.api_token:
            return {
                "final_status": "RECHARGE_FAILED",
                "txid": "",
                "opid": "",
                "raw_msg": "A1TOPUP_TOKEN_NOT_SET_IN_ENV",
            }

        op_code = self.resolve_operator_code(operator, plan_hint=plan_hint)
        amt_str = (
            str(int(amount))
            if amount == amount.to_integral_value()
            else f"{amount:.2f}"
        )

        payload = {
            "token": self.api_token,
            "operatorcode": op_code,
            "number": number,
            "amount": amt_str,
            "orderid": local_order_id,
            "circlecode": "0",
            "format": "json",
        }

        try:
            resp = requests.post(self.base_url, data=payload, timeout=20)
            raw_msg = resp.text[:300]
            try:
                data = resp.json()
            except ValueError:
                data = {}

            st = str(data.get("status", "")).lower()
            txid = str(data.get("txid", ""))
            opid = str(data.get("opid", ""))

            if st == "success":
                final_status = "RECHARGE_SUCCESS"
            elif st in ("pending", "inprogress", "processing", ""):
                final_status = "RECHARGE_PENDING"
            else:
                final_status = "RECHARGE_FAILED"

            return {
                "final_status": final_status,
                "txid": txid,
                "opid": opid,
                "raw_msg": raw_msg,
            }
        except Exception as exc:
            logger.exception("A1Topup execute_recharge failed for %s", local_order_id)
            return {
                "final_status": "RECHARGE_PENDING",
                "txid": "",
                "opid": "",
                "raw_msg": f"A1Topup API Error: {exc}",
            }

    def check_status(self, order_id: str, fallback_txid: str = "") -> Dict[str, Any]:
        resp = requests.get(
            self.status_url,
            params={"token": self.api_token, "orderid": order_id, "format": "json"},
            timeout=15,
        )
        data = resp.json() if resp.content else {}
        st = str(data.get("status", "")).lower()
        opid = str(data.get("opid", ""))
        txid = str(data.get("txid", fallback_txid or ""))

        if st == "success":
            mapped = "SUCCESS"
        elif st in ("failure", "failed", "error", "refund"):
            mapped = "FAILED"
        else:
            mapped = "PENDING"

        return {
            "mapped_status": mapped,
            "txid": txid,
            "opid": opid,
        }
