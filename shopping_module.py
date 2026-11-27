import urllib.parse
from flask import Blueprint, render_template_string, url_for

shopping_bp = Blueprint("shopping_bp", __name__)

KNOWN_STORE_DOMAINS = {
    "myntra": "myntra.com",
    "amazon": "amazon.in",
    "meesho": "meesho.com",
    "flipkart": "flipkart.com",
    "ajio": "ajio.com",
    "ajio direct": "ajio.com",
    "jiomart": "jiomart.com",
    "strch": "strch.in",
    "dot & key": "dotandkey.com",
    "dot & key store": "dotandkey.com",
    "blinkit": "blinkit.com",
    "agoda": "agoda.com",
    "air india": "airindia.com",
    "dell": "dell.com",
    "hamara mall": "hamaramall.com",
    "havells": "havells.com",
    "mivi": "mivi.in",
    "muscleblaze": "muscleblaze.com",
    "oppo": "oppo.com",
    "realme": "realme.com",
    "realme store": "realme.com",
    "shopsy": "shopsy.in",
    "shopsy store": "shopsy.in",
    "swiggy instamart": "swiggy.com",
    "instamart": "swiggy.com",
    "zandu care": "zanduayurveda.com",
    "zandu": "zanduayurveda.com",
    "truemeds": "truemeds.in",
    "truemeds store": "truemeds.in",
    "boat": "boat-lifestyle.com",
    "boat store": "boat-lifestyle.com",
}

AFFILIATE_STORES = [
    {"id": "myntra", "name": "Myntra", "domain": "myntra.com", "url": "https://myntr.it/LlapLAs"},
    {"id": "amazon", "name": "Amazon", "domain": "amazon.in", "url": ""},
    {"id": "meesho", "name": "Meesho", "domain": "meesho.com", "url": ""},
    {"id": "flipkart", "name": "Flipkart", "domain": "flipkart.com", "url": "https://bitli.in/qxwxpy0"},
    {"id": "ajio", "name": "AJIO Direct", "domain": "ajio.com", "url": "https://ajiio.in/S0LOTb3"},
    {"id": "jiomart", "name": "JioMart", "domain": "jiomart.com", "url": "https://bitli.in/sSHJCpW"},
    {"id": "strch", "name": "Strch", "domain": "strch.in", "url": "https://bitli.in/2vzomZh"},
    {"id": "dot_and_key", "name": "Dot & Key Store", "domain": "dotandkey.com", "url": "https://bitli.in/F8jSEnN"},
    {"id": "blinkit", "name": "Blinkit", "domain": "blinkit.com", "url": "https://bitli.in/FkcmIPc"},
    {"id": "agoda", "name": "Agoda", "domain": "agoda.com", "url": "https://bitli.in/Tp3qLrd"},
    {"id": "air_india", "name": "Air India", "domain": "airindia.com", "url": "https://bitli.in/XSsddh8"},
    {"id": "dell", "name": "Dell", "domain": "dell.com", "url": "https://bitli.in/o5Yg8wg"},
    {"id": "hamara_mall", "name": "Hamara Mall", "domain": "hamaramall.com", "url": "https://bitli.in/u5fI6pv"},
    {"id": "havells", "name": "Havells", "domain": "havells.com", "url": "https://bitli.in/9d93h7D"},
    {"id": "mivi", "name": "Mivi", "domain": "mivi.in", "url": "https://bitli.in/ADbtog8"},
    {"id": "muscleblaze", "name": "MuscleBlaze", "domain": "muscleblaze.com", "url": "https://bitli.in/oji4VVi"},
    {"id": "oppo", "name": "Oppo", "domain": "oppo.com", "url": "https://bitli.in/stWRpy9"},
    {"id": "realme", "name": "Realme Store", "domain": "realme.com", "url": "https://bitli.in/jKsRxOr"},
    {"id": "shopsy", "name": "Shopsy Store", "domain": "shopsy.in", "url": "https://bitli.in/LfaJxVd"},
    {"id": "swiggy_instamart", "name": "Swiggy Instamart", "domain": "swiggy.com", "url": "https://bitli.in/4l4aOvi"},
    {"id": "zandu_care", "name": "Zandu Care", "domain": "zanduayurveda.com", "url": "https://bitli.in/Ky21Evt"},
    {"id": "truemeds", "name": "Truemeds Store", "domain": "truemeds.in", "url": "https://bitli.in/aFR9mvP"},
    {"id": "boat", "name": "BoAt store", "domain": "boat-lifestyle.com", "url": "https://bitli.in/hmoTfby"},
]


def _normalize_domain(raw_value: str) -> str:
    value = str(raw_value or "").strip().lower()
    if not value:
        return ""
    if "://" not in value:
        value = "https://" + value
    host = urllib.parse.urlparse(value).netloc.lower().strip()
    return host[4:] if host.startswith("www.") else host


def resolve_store_logo(store_name: str, target_url: str = "", domain: str = "") -> str:
    clean_domain = _normalize_domain(domain)
    if clean_domain and "." in clean_domain:
        return f"https://www.google.com/s2/favicons?domain={urllib.parse.quote(clean_domain)}&sz=128"
    normalized_name = " ".join(str(store_name or "").strip().lower().split())
    if normalized_name in KNOWN_STORE_DOMAINS:
        return f"https://www.google.com/s2/favicons?domain={urllib.parse.quote(KNOWN_STORE_DOMAINS[normalized_name])}&sz=128"
    parsed_host = _normalize_domain(target_url)
    if parsed_host and "." in parsed_host and parsed_host not in {"bitli.in", "myntr.it"}:
        return f"https://www.google.com/s2/favicons?domain={urllib.parse.quote(parsed_host)}&sz=128"
    slug = "".join(ch for ch in normalized_name if ch.isalnum())
    return f"https://www.google.com/s2/favicons?domain={urllib.parse.quote(slug + '.com')}&sz=128" if slug else ""


def get_active_stores():
    active = []
    for store in AFFILIATE_STORES:
        url = str(store.get("url") or "").strip()
        if url:
            item = dict(store)
            item["logo"] = resolve_store_logo(item.get("name", ""), url, item.get("domain", ""))
            active.append(item)
    return active


SHOP_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Commission Cloud</title>
  <style>
    * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    body { margin: 0; background: #f1f5f9; color: #0f172a; }
    .wrap { max-width: 720px; margin: 0 auto; padding: 24px 16px 40px; }

    .top-recharge {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      margin: 8px auto 28px;
      color: #0f172a;
    }
    .round-icon {
      width: 128px;
      height: 128px;
      border-radius: 50%;
      background: linear-gradient(135deg, #7c3aed 0%, #4c1d95 100%);
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 62px;
      box-shadow: 0 10px 24px rgba(109, 40, 217, 0.32);
      border: 4px solid #ffffff;
      transition: transform 0.18s ease;
    }
    .top-recharge:hover .round-icon { transform: scale(1.05); }
    .round-label {
      margin-top: 10px;
      font-size: 16px;
      font-weight: 800;
      color: #3b0764;
    }

    .store-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
    .store-item {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      padding: 14px 10px;
      text-align: center;
      text-decoration: none;
      color: #0f172a;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .store-item img { width: 38px; height: 38px; object-fit: contain; margin-bottom: 8px; }
    .store-name { font-size: 13px; font-weight: 700; }
  </style>
</head>
<body>
  <div class="wrap">
    <a href="{{ recharge_url }}" class="top-recharge">
      <div class="round-icon">📱</div>
      <div class="round-label">Mobile Recharge</div>
    </a>

    <div class="store-list">
      {% for s in stores %}
      <a href="{{ s.url }}" target="_blank" rel="noopener noreferrer" class="store-item">
        <img src="{{ s.logo }}" alt="{{ s.name }}" onerror="this.style.display='none';">
        <div class="store-name">{{ s.name }}</div>
      </a>
      {% endfor %}
    </div>
  </div>
</body>
</html>
"""


@shopping_bp.route("/")
def shop_home():
    return render_template_string(
        SHOP_PAGE_HTML,
        stores=get_active_stores(),
        recharge_url=url_for("recharge_bp.recharge_home"),
    )
