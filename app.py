from flask import Flask, render_template
import requests, os, json
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)
DATA_FOLDER = "data"

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

USER = "hung1"
URL = "https://boeingvip.xyz/gambler/user/child/statistic"

# ===== TIMEZONE VN =====
def get_vn_time():
    return datetime.utcnow() + timedelta(hours=7)

# ===== FETCH DATA =====
def fetch_data():
    now_vn = get_vn_time()

    # đầu tháng VN
    start_vn = datetime(now_vn.year, now_vn.month, 1)

    # convert sang UTC để gọi API
    start_utc = start_vn - timedelta(hours=7)
    end_utc = now_vn - timedelta(hours=7)

    payload = {
        "shopId": None,
        "packageName": "",
        "assigned": USER,
        "productId": "",
        "action": "import_token",
        "startDate": start_utc.isoformat() + "Z",
        "endDate": end_utc.isoformat() + "Z"
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://boeingvip.xyz",
        "Referer": f"https://boeingvip.xyz/thong-ke-nap?user={USER}",
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.post(URL, json=payload, headers=headers)
    data = r.json()

    result = defaultdict(lambda: {"price": 0, "count": 0})
    total = 0

    for item in data.get("data", []):
        game = item.get("gameName", "Unknown")

        price = float(str(item.get("price", "0")).replace("$", "").replace(",", ""))
        count = int(item.get("count", 0))

        money = price * count

        result[game]["price"] += money
        result[game]["count"] += count
        total += money

    return result, total, data.get("data", [])

# ===== SAVE TODAY =====
def save_today(items, total):
    today = get_vn_time().date()
    today_file = os.path.join(DATA_FOLDER, f"{today}.json")

    with open(today_file, "w", encoding="utf-8") as f:
        json.dump({
            "items": items,
            "total": total
        }, f, ensure_ascii=False, indent=2)

# ===== LOAD HISTORY =====
def load_history():
    history = {}

    for file in os.listdir(DATA_FOLDER):
        if file.endswith(".json"):
            path = os.path.join(DATA_FOLDER, file)

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

                total = data.get("total", 0)
                day = file.replace(".json", "")

                history[day] = total

    return dict(sorted(history.items()))

# ===== ROUTE =====
@app.route("/")
def index():
    result, total_today, items = fetch_data()
    save_today(items, total_today)
    history = load_history()

    return render_template(
        "index.html",
        result=result,
        total=total_today,
        history=history
    )

# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)
