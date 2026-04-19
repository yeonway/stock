from flask import Flask, render_template, request, redirect, url_for
import json
import os
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

STOCKS = [
    {"code": "005930", "name": "삼성전자"},
    {"code": "035720", "name": "카카오"},
    {"code": "035420", "name": "NAVER"},
]

PRICE_SAMPLE = {
    "005930": [72000, 73000, 74000, 73500, 74500, 75000, 76000],
    "035720": [54000, 55000, 56000, 55500, 56500, 57000, 57500],
    "035420": [170000, 171000, 172000, 171500, 172500, 173000, 173500],
}

def predict_next_price(prices):
    days = np.arange(len(prices)).reshape(-1, 1)
    prices = np.array(prices)
    model = LinearRegression()
    model.fit(days, prices)
    next_day = np.array([[len(prices)]])
    predicted_price = model.predict(next_day)[0]
    return predicted_price

@app.route("/", methods=["GET", "POST"])
def select_stocks():
    if request.method == "POST":
        selected_codes = request.form.getlist("stocks")
        selected = [stock for stock in STOCKS if stock["code"] in selected_codes]
        with open("selected_stocks.json", "w", encoding="utf-8") as f:
            json.dump(selected, f, ensure_ascii=False, indent=2)
        return redirect(url_for("show_selected"))
    return render_template("select.html", stocks=STOCKS)

@app.route("/selected")
def show_selected():
    selected = []
    ai_results = []
    if os.path.exists("selected_stocks.json"):
        with open("selected_stocks.json", encoding="utf-8") as f:
            selected = json.load(f)
        for stock in selected:
            prices = PRICE_SAMPLE.get(stock["code"], [])
            ai_pred = predict_next_price(prices) if prices else None
            ai_results.append({
                "name": stock["name"],
                "code": stock["code"],
                "latest_price": prices[-1] if prices else "데이터 없음",
                "ai_pred": round(ai_pred, 2) if ai_pred else "예측불가"
            })
    return render_template("selected.html", selected=selected, ai_results=ai_results)

if __name__ == "__main__":
    app.run()