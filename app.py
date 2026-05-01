from flask import Flask, render_template, request
import requests
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)

# ✅ API MỚI
URL = "https://boeingvip.xyz/gambler/user/child/statistic"
USER = "hung2"

def fetch_data(start_date, end_date, start_time, end_time):

    # ===== PARSE GIỜ VN =====
    start_local = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M:%S")
    end_local = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M:%S")

    # ===== CONVERT UTC =====
    start_utc = start_local - timedelta(hours=7)
    end_utc = end_local - timedelta(hours=7)

    # ===== FORMAT CHUẨN API =====
    start_utc_str = start_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_utc_str = end_utc.strftime("%Y-%m-%dT%H:%M:%S.999Z")

    payload = {
        "shopId": None,
        "packageName": "",
        "assigned": USER,
        "productId": "",
        "action": "import_token",
        "startDate": start_utc_str,
        "endDate": end_utc_str
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://boeingvip.xyz",
        "Referer": f"https://boeingvip.xyz/thong-ke-nap?user={USER}",
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        r = requests.post(URL, json=payload, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json().get("data", [])
    except Exception as e:
        print("API ERROR:", e)
        data = []

    result = defaultdict(lambda: {"price": 0, "count": 0})
    total = 0

    for item in data:
        game = item.get("gameName", "Unknown")

        try:
            price = float(item["price"].replace("$", "").replace(",", ""))
            count = int(item["count"])
        except:
            price = 0
            count = 0

        money = price * count

        result[game]["price"] += money
        result[game]["count"] += count
        total += money

    result = dict(sorted(result.items(), key=lambda x: x[1]["price"], reverse=True))

    return result, total


@app.route("/")
def index():

    now = datetime.utcnow() + timedelta(hours=7)

    start_date = request.args.get("start_date") or now.strftime("%Y-%m-%d")
    end_date = request.args.get("end_date") or now.strftime("%Y-%m-%d")

    start_time = request.args.get("start_time") or "00:00:00"
    end_time = request.args.get("end_time") or "23:59:59"

    result, total = fetch_data(start_date, end_date, start_time, end_time)

    return render_template(
        "index.html",
        result=result,
        total=total,
        start_date=start_date,
        end_date=end_date,
        start_time=start_time,
        end_time=end_time,
        user_name="Bú Bú"
    )


if __name__ == "__main__":
    app.run(debug=True)
