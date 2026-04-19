# 파일명: main.py
# 1. 주식 데이터 크롤링 → 2. 머신러닝 분석 → 3. 이메일로 결과 자동 발송

import requests
from bs4 import BeautifulSoup
import numpy as np
from sklearn.linear_model import LinearRegression
import smtplib
from email.mime.text import MIMEText

def get_stock_price(code):
    """
    네이버 금융에서 현재가 크롤링
    """
    url = f'https://finance.naver.com/item/main.naver?code={code}'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    price_tag = soup.select_one('p.no_today .blind')
    price = price_tag.text if price_tag else "N/A"
    return price

def predict_next_price(prices):
    """
    최근 가격(prices)으로 내일 가격 머신러닝(선형회귀) 예측
    """
    days = np.arange(len(prices)).reshape(-1, 1)
    prices = np.array(prices)
    model = LinearRegression()
    model.fit(days, prices)
    next_day = np.array([[len(prices)]])
    predicted_price = model.predict(next_day)[0]
    return predicted_price

def send_email(subject, body, to_email):
    """
    이메일(subject, body)을 to_email로 발송 (구글 SMTP)
    """
    from_email = 'your_email@gmail.com'
    password = 'your_password'
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())

if __name__ == "__main__":
    code = '005930'  # 삼성전자
    price = get_stock_price(code)
    
    # 최근 7일 가격 예시 (실전에서는 여러 날 크롤링 필요)
    prices = [72000, 73000, 74000, 73500, 74500, 75000, int(price.replace(',', ''))]
    pred = predict_next_price(prices)
    
    message = (
        f"삼성전자({code}) 오늘 가격: {price}원\n"
        f"머신러닝(선형회귀) 예측, 내일 예상 가격: {round(pred, 2)}원"
    )
    
    send_email("오늘의 주식 AI 분석 결과", message, "받는사람@example.com")