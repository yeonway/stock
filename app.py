from flask import Flask, render_template_string, request, redirect, send_file
import os, json
from datetime import date

app = Flask(__name__)
app.secret_key = 'secret_for_session_0321'

DATA_FILE = "data.json"

def init_data(cash):
    return {
        "cash": cash,
        "records": [],
        "stocks": {}
    }

def read_data():
    if not os.path.exists(DATA_FILE):
        return None
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

TEMPLATE_START = """
<!doctype html><html lang="ko"><head>
<meta charset="utf-8"><title>📒 가상 투자일기</title>
<meta name="viewport" content="width=440, initial-scale=1.0">
<style>
body { background:#f5f6fa; font-family:sans-serif;}
.container{max-width:420px; margin:50px auto; background:#fff; border-radius:18px; box-shadow:0 4px 16px #0001; padding:32px 22px;}
input[type=number],input[type=text] {width:100%;padding:10px 8px; margin-bottom:15px; border:1px solid #ccd; border-radius:9px; font-size:1.1em;}
button{width:100%;padding:13px 0; border:none; border-radius:9px; background:#0078ff; color:#fff; font-size:1.2em; font-weight:bold;}
h1{text-align:center; margin-bottom:24px;}
label{font-size:1.1em;}
@media (max-width:440px){.container{margin:0;border-radius:0;}}
</style>
</head>
<body>
<div class="container">
<h1>📒 가상 투자일기</h1>
<form method="POST">
    <label>🪙 시작할 가상 자본(원):</label>
    <input type="number" name="start_cash" min="10000" max="100000000" step="1000" value="1000000" required>
    <button type="submit">시작하기</button>
</form>
</div>
</body></html>
"""

TEMPLATE_MAIN = """
<!doctype html><html lang="ko"><head>
<meta charset="utf-8"><title>📒 가상 투자일기</title>
<meta name="viewport" content="width=440, initial-scale=1.0">
<style>
body { background:#f5f6fa; font-family:sans-serif;}
.container{max-width:500px; margin:30px auto; background:#fff; border-radius:18px; box-shadow:0 4px 16px #0001; padding:30px 18px;}
h1 {text-align:center;}
input,textarea,select { width:100%; margin-bottom:10px; padding:8px; border-radius:7px; border:1px solid #ccc; font-size:1em;}
textarea { min-height:38px; max-height:360px; overflow-y:hidden; resize:none; transition:.15s;}
button {width:100%; padding:10px; border-radius:8px; background:#0078ff; color:#fff; font-size:1.1em; font-weight:bold; border:none;}
th,td {padding:5px 9px; border-bottom:1px solid #e2e8f0;}
.stocktbl {width:100%; margin-bottom:16px; border-collapse:collapse;}
th {background:#e3eefc;}
tr:last-child td {border-bottom:none;}
tr:hover {background:#f0f6fd;}
hr{margin:25px 0 12px 0;}
.err{color:#c23; font-weight:bold; margin:12px 0;}
@media (max-width:510px){.container{margin:0;border-radius:0;}}
.actionbtn { background:#55b053; margin-bottom:6px; }
.actionbtn2 { background:#fdbb30; color:#222; }
.actionbtn3 { background:#575a; }
</style>
<script>
window.onload = function(){
  document.querySelectorAll('textarea').forEach(function(t){
    function autoResize(){
      t.style.height = 'auto';
      t.style.height = (t.scrollHeight)+'px';
    }
    t.addEventListener('input', autoResize);
    autoResize();
  });
};
</script>
</head>
<body>
<div class="container">
<h1>📒 가상 투자일기</h1>

<div style="background:#f4f9ff; border-radius:10px; padding:11px 13px; margin-bottom:16px;">
  <b>💰 내 가상 현금: <span style="font-size:1.1em; color:#2e7;">{{cash}}원</span></b>
</div>
{% if err %}<div class="err">{{err}}</div>{% endif %}

<form method="POST">
  <input type="hidden" name="action" value="buy">
  <h3 style="margin-bottom:7px;">🟢 주식/ETF 매수</h3>
  <input name="date" type="date" required value="{{today}}">
  <input name="name" placeholder="종목/ETF명" required>
  <input name="cnt" type="number" min="1" placeholder="매수 수량(주)" required>
  <input name="price" type="number" min="1" placeholder="매수가(원)" required>
  <textarea name="why" placeholder="투자 이유(한줄~여러줄 가능)" required></textarea>
  <textarea name="news" placeholder="오늘 시장/뉴스 (여러줄)"></textarea>
  <textarea name="memo" placeholder="내 생각/상상 결과 (여러줄)" rows="2"></textarea>
  <button>매수 기록 저장</button>
</form>

<form method="POST">
  <input type="hidden" name="action" value="sell">
  <h3 style="margin-top:13px; margin-bottom:7px;">🔴 주식/ETF 매도</h3>
  <select name="name" required>
    <option value="" disabled selected>종목명 선택</option>
    {% for s,v in stocks.items() %}
      <option value="{{s}}">{{s}} ({{v["cnt"]}}주 보유)</option>
    {% endfor %}
  </select>
  <input name="cnt" type="number" min="1" placeholder="매도 수량(주)" required>
  <input name="price" type="number" min="1" placeholder="매도가(원)" required>
  <textarea name="memo" placeholder="매도 이유/메모 (여러줄)" rows="2"></textarea>
  <button class="actionbtn2" style="margin-bottom:16px;">매도 기록 저장</button>
</form>

<form method="POST">
  <input type="hidden" name="action" value="deposit">
  <h3 style="margin-top:13px; margin-bottom:7px;">➕ 자본 입금(가상 잔고 추가)</h3>
  <input name="deposit" type="number" min="1000" placeholder="입금할 금액(원)" required>
  <textarea name="memo" placeholder="입금 사유/메모 (선택)" rows="1"></textarea>
  <button class="actionbtn">입금</button>
</form>

<h3>📊 내 가상 주식 보유내역</h3>
<table class="stocktbl">
  <tr><th>종목명</th><th>수량(주)</th><th>평균매입가</th><th>총투입금액</th></tr>
  {% for s,v in stocks.items() %}
    <tr>
      <td>{{s}}</td>
      <td>{{v["cnt"]}}</td>
      <td>{{"{:,}".format(v["price"])}}</td>
      <td>{{"{:,}".format(v["total"])}}</td>
    </tr>
  {% else %}
    <tr><td colspan=4 style="color:#aaa;">(보유종목 없음)</td></tr>
  {% endfor %}
</table>

<hr>
<div class="list">
  <h3>🗒️ 내 투자일기</h3>
  {% if records %}
    {% for it in records %}
      <div class="item" style="background:#f7faff; margin-bottom:14px; padding:14px 10px; border-radius:11px;white-space:pre-line;">
        <b>{{it["date"]}}</b> {{it.get("name","")}}
        {% if it["type"]=="매수" %}
          <span style="color:#0a4;">[매수]</span> {{it["cnt"]}}주 × {{it["price"]}}원<br>
          <span style="color:#1d5;">이유:</span> {{it.get("why","")|replace('\n','<br>')}}<br>
          <span style="color:#15a;">시장/뉴스:</span> {{it.get("news","")|replace('\n','<br>')}}<br>
        {% elif it["type"]=="매도" %}
          <span style="color:#e00;">[매도]</span> {{it["cnt"]}}주 × {{it["price"]}}원<br>
        {% elif it["type"]=="입금" %}
          <span style="color:#3aa6fd;">[입금]</span> {{it["amount"]}}원<br>
        {% endif %}
        <span style="color:#789;">{{it.get("memo","")|replace('\n','<br>')}}</span>
      </div>
    {% endfor %}
  {% else %}
    <div style="color:#888;">아직 기록이 없어요!</div>
  {% endif %}
</div>

<form method="POST" action="/reset" onsubmit='return confirm("정말 모든 기록을 초기화할까요?");'>
  <button class="actionbtn3" style="margin-top:22px;">🔄 데이터 전체 초기화</button>
</form>
<form method="GET" action="/download">
  <button style="background:#3aa6fd; margin-top:8px;">⬇️ JSON 파일로 내보내기</button>
</form>
<form method="POST" enctype="multipart/form-data" action="/upload">
  <input type="file" name="file" accept=".json" required>
  <button style="background:#3ac6bd;">⬆️ JSON 파일 불러오기</button>
</form>

</div>
</body></html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    data = read_data()
    if data is None:
        if request.method == "POST":
            cash = int(request.form.get("start_cash", 1000000))
            save_data(init_data(cash))
            return redirect("/")
        return render_template_string(TEMPLATE_START)
    err = None
    if request.method == "POST":
        action = request.form.get("action", "buy")
        try:
            if action == "buy":
                datev = request.form["date"]
                name = request.form["name"]
                cnt = int(request.form["cnt"])
                price = int(request.form["price"])
                why = request.form["why"]
                news = request.form.get("news","")
                memo = request.form.get("memo","")
                cost = cnt * price
                if data["cash"] < cost:
                    err = "잔액 부족! (남은 돈: {}원, 필요금액: {}원)".format(data["cash"], cost)
                else:
                    rec = {
                        "type": "매수",
                        "date": datev,
                        "name": name,
                        "cnt": cnt,
                        "price": price,
                        "why": why,
                        "news": news,
                        "memo": memo,
                    }
                    data["records"].append(rec)
                    stocks = data["stocks"]
                    if name in stocks:
                        old = stocks[name]
                        total_cnt = old["cnt"] + cnt
                        avg_price = int(round((old["price"]*old["cnt"] + price*cnt) / total_cnt))
                        total_invest = old["total"] + cost
                        stocks[name] = {"cnt": total_cnt, "price": avg_price, "total": total_invest}
                    else:
                        stocks[name] = {"cnt": cnt, "price": price, "total": cost}
                    data["cash"] -= cost
                    save_data(data)
                    return redirect("/")
            elif action == "sell":
                name = request.form["name"]
                cnt = int(request.form["cnt"])
                price = int(request.form["price"])
                memo = request.form.get("memo","")
                stocks = data["stocks"]
                if name not in stocks or stocks[name]["cnt"] < cnt:
                    err = "매도 가능한 주식 수량이 부족합니다!"
                else:
                    total_sale = cnt * price
                    rec = {
                        "type": "매도",
                        "date": str(date.today()),
                        "name": name,
                        "cnt": cnt,
                        "price": price,
                        "memo": memo,
                    }
                    data["records"].append(rec)
                    old = stocks[name]
                    left_cnt = old["cnt"] - cnt
                    left_total = old["total"] - int(old["price"] * cnt)
                    if left_cnt > 0:
                        stocks[name] = {
                            "cnt": left_cnt,
                            "price": old["price"],
                            "total": left_total
                        }
                    else:
                        del stocks[name]
                    data["cash"] += total_sale
                    save_data(data)
                    return redirect("/")
            elif action == "deposit":
                amount = int(request.form["deposit"])
                memo = request.form.get("memo","")
                data["cash"] += amount
                rec = {
                    "type": "입금",
                    "date": str(date.today()),
                    "amount": amount,
                    "memo": memo,
                }
                data["records"].append(rec)
                save_data(data)
                return redirect("/")
        except Exception as e:
            err = f"오류: {e}"
    return render_template_string(
        TEMPLATE_MAIN,
        cash=data["cash"],
        records=data["records"][::-1],
        stocks=data["stocks"],
        today=str(date.today()),
        err=err
    )

@app.route("/reset", methods=["POST"])
def reset():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    return redirect("/")

@app.route("/download")
def download():
    return send_file(DATA_FILE, as_attachment=True)

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files['file']
    try:
        data = json.load(f)
        if not isinstance(data, dict) or not all(k in data for k in ("cash","records","stocks")):
            raise ValueError("잘못된 데이터 포맷입니다.")
        save_data(data)
    except Exception as e:
        pass
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
