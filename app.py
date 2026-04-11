from flask import Flask, render_template, request
import requests
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)

USER = "hung1"
URL = "https://boeingvip.xyz/gambler/user/child/statistic"

# ===== TIME VN =====
def get_vn_time():
    return datetime.utcnow() + timedelta(hours=7)

# ===== FETCH DATA =====
def fetch_data(start_vn, end_vn):
    result = defaultdict(lambda: {"price": 0, "count": 0})
    total = 0

    try:
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
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.post(URL, json=payload, headers=headers, timeout=10)

        if r.status_code != 200:
            print("API lỗi:", r.text)
            return result, total

        try:
            data = r.json()
        except:
            print("JSON lỗi")
            return result, total

        for item in data.get("data", []):
            try:
                game = item.get("gameName", "Unknown")

                price = float(str(item.get("price", "0")).replace("$", "").replace(",", ""))
                count = int(item.get("count", 0))

                money = price * count

                result[game]["price"] += money
                result[game]["count"] += count
                total += money
            except:
                continue

    except Exception as e:
        print("FETCH ERROR:", e)

    return result, total


# ===== ROUTE =====
@app.route("/")
def index():
    now = get_vn_time()

    start_vn = datetime(now.year, now.month, now.day)
    end_vn = start_vn + timedelta(days=1)

    result, total = fetch_data(start_vn, end_vn)

    return render_template(
        "index.html",
        result=result,
        total=total
    )


if __name__ == "__main__":
    app.run(debug=True)
