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

# ===== FETCH DATA (SIÊU AN TOÀN) =====
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
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.post(URL, json=payload, headers=headers, timeout=10)

        # nếu API lỗi → không crash
        if r.status_code != 200:
            print("API lỗi:", r.text)
            return result, total

        try:
            data = r.json()
        except:
            print("API trả không phải JSON")
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

            except Exception as e:
                print("Lỗi item:", e)
                continue

    except Exception as e:
        print("Lỗi fetch:", e)

    return result, total


# ===== ROUTE =====
@app.route("/")
def index():
    try:
        date_str = request.args.get("date")
        mode = request.args.get("mode", "day")

        now = get_vn_time()

        if date_str:
            selected = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            selected = now

        start_vn = datetime(selected.year, selected.month, selected.day)
        end_vn = start_vn + timedelta(days=1)

        result, total = fetch_data(start_vn, end_vn)

        return render_template(
            "index.html",
            result=result,
            total=total,
            selected_date=start_vn.strftime("%Y-%m-%d"),
            mode=mode
        )

    except Exception as e:
        print("Lỗi route:", e)
        return "Server đang lỗi, check log", 500


# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)
