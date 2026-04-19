# 파일명: stock_crawling.py
# 네이버 금융에서 주식 가격을 크롤링하는 코드 예시

import requests
from bs4 import BeautifulSoup

def get_stock_price(code):
    """
    주어진 종목 코드(code)에 대해 네이버 금융에서 현재가를 가져옵니다.
    예: 삼성전자 '005930'
    """
    url = f'https://finance.naver.com/item/main.naver?code={code}'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    price_tag = soup.select_one('p.no_today .blind')  # 현재가가 들어있는 태그 선택
    price = price_tag.text if price_tag else "N/A"
    return price

# 삼성전자(005930) 가격 출력
if __name__ == "__main__":
    print(get_stock_price('005930'))