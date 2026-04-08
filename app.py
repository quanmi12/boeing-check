from flask import Flask, render_template, request
import requests, os, json
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)
DATA_FOLDER = "data"

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

USER = "hung1"
URL = "https://boeingvip.xyz/gambler/user/child/statistic"

def get_vn_time():
    return datetime.utcnow() + timedelta(hours=7)

# ===== FETCH DATA THEO NGÀY =====
def fetch_data(start_vn, end_vn):
    start_utc = start_vn - timedelta(hours=7)
    end_utc = end_vn - timedelta(hours=7)

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

def save_today(items, total, date):
    today_file = os.path.join(DATA_FOLDER, f"{date}.json")

    with open(today_file, "w", encoding="utf-8") as f:
        json.dump({
            "items": items,
            "total": total
        }, f, ensure_ascii=False, indent=2)

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

@app.route("/")
def index():
    date_str = request.args.get("date")

    if date_str:
        # chọn ngày
        selected_date = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        selected_date = get_vn_time()

    # 00:00 → 23:59 của ngày đó
    start_vn = datetime(selected_date.year, selected_date.month, selected_date.day)
    end_vn = start_vn + timedelta(days=1)

    result, total_today, items = fetch_data(start_vn, end_vn)

    save_today(items, total_today, start_vn.date())
    history = load_history()

    return render_template(
        "index.html",
        result=result,
        total=total_today,
        history=history,
        selected_date=start_vn.strftime("%Y-%m-%d")
    )

if __name__ == "__main__":
    app.run(debug=True)
