# 파일명: stock_analysis.py
# 주식 가격 데이터의 이동평균을 계산하는 코드 예시

import pandas as pd

def simple_moving_average(prices, window=5):
    """
    주어진 가격 리스트(prices)에 대해 window 크기만큼 이동평균을 계산합니다.
    기본값은 5일 이동평균입니다.
    """
    return pd.Series(prices).rolling(window).mean().tolist()

if __name__ == "__main__":
    prices = [72000, 73000, 74000, 73500, 74500, 75000, 76000]
    ma = simple_moving_average(prices)
    print("5일 이동평균:", ma)