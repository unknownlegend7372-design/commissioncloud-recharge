import logging
import os
import re
import secrets
import sqlite3
from dotenv import load_dotenv
from flask import Flask, request, jsonify, url_for, render_template_string

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# recharge और shopping मॉड्यूल से ब्लूप्रिंट इम्पोर्ट करें
from recharge.recharge import recharge_bp
from shopping_module import shopping_bp

logger = logging.getLogger("recharge.app")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)

ORDERS_DB_PATH = os.path.join(BASE_DIR, "recharge", "recharge_orders.db")

LEGAL_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }} - Commission Cloud</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f4f6f9; color: #1f2937; margin: 0; padding: 0; line-height: 1.65; }
    header { background: #0f172a; color: #fff; padding: 16px 20px; text-align: center; }
    header a { color: #fff; text-decoration: none; font-size: 20px; font-weight: bold; }
    .container { max-width: 860px; margin: 24px auto; background: #fff; padding: 28px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); }
    h1 { color: #0f172a; margin-top: 0; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }
    h2 { color: #1e293b; font-size: 18px; margin-top: 22px; }
    p, li { font-size: 15px; color: #374151; }
    footer { text-align: center; padding: 20px; font-size: 14px; color: #4b5563; border-top: 1px solid #e5e7eb; margin-top: 30px; }
    footer a { color: #2563eb; text-decoration: none; margin: 0 10px; }
  </style>
</head>
<body>
  <header>
    <a href="/">Commission Cloud (commissioncloud.in)</a>
  </header>
  <div class="container">
    <h1>{{ title }}</h1>
    <p><strong>Effective Date:</strong> November 2026 | <strong>Platform:</strong> Commission Cloud (https://commissioncloud.in)</p>
    {{ content | safe }}
  </div>
  <footer>
    <a href="/">Home / Recharge</a> |
    <a href="/privacy-policy">Privacy Policy</a> |
    <a href="/terms">Terms &amp; Conditions</a> |
    <a href="/refund-policy">Refund &amp; Cancellation Policy</a> |
    <a href="/contact">Contact Us</a>
    <p style="margin-top:10px;">&copy; 2026 Commission Cloud. All Rights Reserved.</p>
  </footer>
</body>
</html>
"""


def get_orders_conn():
    conn = sqlite3.connect(ORDERS_DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def extract_plan_amount_from_text(plan_text: str) -> float:
    text = plan_text or ""
    m = re.search(r"(?:₹|rs\.?|inr)\s*([0-9]+(?:\.[0-9]{1,2})?)", text, flags=re.IGNORECASE)
    if not m:
        m = re.search(r"\b([0-9]{1,5}(?:\.[0-9]{1,2})?)\s*(?:\/-|\/[0-9]+\s*d)", text, flags=re.IGNORECASE)
    if m:
        try:
            val = round(float(m.group(1)), 2)
            return val if val > 0 else 0.0
        except ValueError:
            return 0.0
    return 0.0


@app.route("/privacy-policy")
def privacy_policy():
    content = """
    <h2>1. Information We Collect</h2>
    <p>Commission Cloud (<strong>commissioncloud.in</strong>) collects essential information required to process prepaid mobile recharges, DTH recharges, utility bill payments, and cashback rewards. This may include your mobile number, subscriber/consumer ID, email address, order ID, and payment transaction reference (UTR/Transaction ID).</p>
    <h2>2. How We Use Information</h2>
    <ul>
      <li>To process and complete recharge and bill payment orders through authorized operator/biller gateways.</li>
      <li>To credit eligible cashback or refunds to your platform wallet and provide customer support.</li>
      <li>To prevent duplicate transactions, fraud, and unauthorized access.</li>
    </ul>
    <h2>3. Data Security &amp; Sharing</h2>
    <p>We do not sell or rent user personal information to third parties. Necessary transaction parameters (such as operator code, subscriber number, and amount) are shared strictly with authorized telecom/biller APIs and payment verification systems solely to fulfill your order.</p>
    <h2>4. Cookies &amp; Session Data</h2>
    <p>We use secure session cookies to maintain user sessions, wallet balances, and CSRF protection during transactions.</p>
    <h2>5. Contact for Privacy Queries</h2>
    <p>For any questions regarding your data or privacy, reach us at <strong>amitkr5993@gmail.com</strong>.</p>
    """
    return render_template_string(LEGAL_PAGE_TEMPLATE, title="Privacy Policy", content=content)


@app.route("/terms")
def terms_and_conditions():
    content = """
    <h2>1. Acceptance of Terms</h2>
    <p>By accessing and using <strong>Commission Cloud</strong> (<strong>https://commissioncloud.in</strong>), you agree to comply with these Terms &amp; Conditions.</p>
    <h2>2. Services Offered</h2>
    <p>Commission Cloud provides an online digital portal for Mobile Prepaid Recharge, DTH Recharge, Electricity, Gas, FASTag bill payments, and promotional cashback rewards.</p>
    <h2>3. User Responsibility</h2>
    <ul>
      <li>Users must verify the mobile number, operator, circle, consumer ID, and recharge/bill amount before initiating payment.</li>
      <li>Commission Cloud is not responsible for recharges or bill payments processed against an incorrect number or wrong operator entered by the user.</li>
    </ul>
    <h2>4. Cashback &amp; Wallet Rules</h2>
    <p>Cashback rates vary by operator and service category and are credited only upon successful completion of the transaction. Wallet balances are usable for eligible services on the platform.</p>
    <h2>5. Service Availability &amp; Modifications</h2>
    <p>Transaction execution depends on telecom operators, billers, and banking networks. Commission Cloud reserves the right to update service terms, cashback rates, or platform policies at any time.</p>
    """
    return render_template_string(LEGAL_PAGE_TEMPLATE, title="Terms & Conditions", content=content)


@app.route("/refund-policy")
def refund_policy():
    content = """
    <h2>1. Completed / Successful Orders</h2>
    <p>All successful mobile recharges, DTH recharges, and utility bill payments are final. Once an order is marked <strong>Success</strong> by the operator or biller, it cannot be cancelled, reversed, or refunded.</p>
    <h2>2. Failed or Rejected Transactions</h2>
    <p>If payment is deducted from your account and the recharge or bill payment fails or is rejected by the operator, the full paid amount (including any wallet amount used) is eligible for refund.</p>
    <h2>3. Refund Timeline &amp; Mode</h2>
    <ul>
      <li><strong>Platform Wallet Refund:</strong> Automatically or manually credited to your Commission Cloud wallet within 1 to 24 hours after failure confirmation.</li>
      <li><strong>Source / Bank Refund:</strong> Where applicable for verified failed gateway payments, refunds are processed within <strong>3 to 7 working days</strong> depending on bank/UPI settlement timelines.</li>
    </ul>
    <h2>4. Pending Orders &amp; Support</h2>
    <p>Orders in <em>Pending</em> status are reconciled with operator status callbacks. If an order remains unresolved beyond 24 hours, please contact <strong>amitkr5993@gmail.com</strong> with your Order ID and UTR/Transaction ID.</p>
    """
    return render_template_string(LEGAL_PAGE_TEMPLATE, title="Refund & Cancellation Policy", content=content)


@app.route("/contact")
def contact_us():
    content = """
    <h2>Customer &amp; Merchant Support</h2>
    <p>For recharge support, payment verification, refund assistance, or business inquiries regarding <strong>Commission Cloud</strong>, please contact us using the details below:</p>
    <ul>
      <li><strong>Brand / Portal Name:</strong> Commission Cloud (Commission Cloud Recharge)</li>
      <li><strong>Website:</strong> https://commissioncloud.in</li>
      <li><strong>Support Email:</strong> amitkr5993@gmail.com</li>
      <li><strong>Operating Hours:</strong> Monday to Saturday, 10:00 AM – 7:00 PM IST</li>
      <li><strong>Location:</strong> Vaishali, Bihar, India</li>
    </ul>
    """
    return render_template_string(LEGAL_PAGE_TEMPLATE, title="Contact Us", content=content)


# ऑपरेटर एपीआई
@app.route('/get-operators')
def get_operators():
    service_type = (request.args.get('service_type') or 'Mobile Prepaid').strip()
    op_list = []

    if 'Mobile' in service_type or 'Prepaid' in service_type:
        conn = None
        try:
            conn = get_orders_conn()
            c = conn.cursor()
            c.execute(
                """SELECT DISTINCT operator FROM operator_plans
                   WHERE LOWER(operator) IN ('jio', 'airtel', 'vi', 'bsnl', 'bsnl combo', 'bsnl topup', 'bsnl_stv')"""
            )
            rows = c.fetchall()
            op_list = [r[0] for r in rows if r[0]]
        except Exception:
            logger.exception("Failed to fetch operators")
            op_list = []
        finally:
            if conn:
                conn.close()

        if not op_list:
            op_list = ["Jio", "Airtel", "Vi", "BSNL Combo", "BSNL Topup"]

    return jsonify(op_list)


@app.route('/get-plans')
def get_plans():
    operator = (request.args.get('operator') or 'Jio').strip()
    plans_list = []
    conn = None

    try:
        conn = get_orders_conn()
        c = conn.cursor()
        if operator.lower().startswith("bsnl"):
            c.execute("SELECT * FROM operator_plans WHERE LOWER(operator) LIKE 'bsnl%' ORDER BY id DESC")
        else:
            c.execute("SELECT * FROM operator_plans WHERE LOWER(operator) = LOWER(?) ORDER BY id DESC", (operator,))
        rows = c.fetchall()

        for r in rows:
            plan_txt = r['plan_text'] or ""
            plans_list.append({
                'id': r['id'],
                'operator': r['operator'],
                'circle': 'Bihar',
                'category': r['category'],
                'amount': extract_plan_amount_from_text(plan_txt),
                'validity': 'NA',
                'data_limit': 'NA',
                'sms_limit': 'NA',
                'description': plan_txt
            })
    except Exception:
        logger.exception("Failed to fetch plans for operator %s", operator)
        plans_list = []
    finally:
        if conn:
            conn.close()

    return jsonify(plans_list)


app.register_blueprint(recharge_bp)
app.register_blueprint(shopping_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    is_debug = os.getenv("FLASK_DEBUG", "0").strip() == "1"
    app.run(host="0.0.0.0", debug=is_debug, port=port)
