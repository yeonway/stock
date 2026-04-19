# 파일명: notify_email.py
# 이메일로 주식 분석 결과를 전송하는 코드 예시

import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, to_email):
    """
    이메일(subject, body)을 to_email로 발송합니다.
    구글 SMTP 사용(계정 정보 필요).
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
    send_email("오늘의 주식 분석 결과", "삼성전자 5일 이동평균: 74500원", "받는사람@example.com")