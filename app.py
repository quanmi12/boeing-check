@app.route("/")
def index():
    date_str = request.args.get("date")
    mode = request.args.get("mode", "day")  # day | month

    now = get_vn_time()

    if mode == "month":
        # 👉 cả tháng hiện tại
        start_vn = datetime(now.year, now.month, 1)
        end_vn = start_vn + timedelta(days=32)
        end_vn = datetime(end_vn.year, end_vn.month, 1)

        selected_date = now.strftime("%Y-%m")

    else:
        # 👉 theo ngày
        if date_str:
            selected = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            selected = now

        start_vn = datetime(selected.year, selected.month, selected.day)
        end_vn = start_vn + timedelta(days=1)

        selected_date = start_vn.strftime("%Y-%m-%d")

    result, total_today, items = fetch_data(start_vn, end_vn)

    save_today(items, total_today, start_vn.date())
    history = load_history()

    return render_template(
        "index.html",
        result=result,
        total=total_today,
        history=history,
        selected_date=selected_date,
        mode=mode
    )
