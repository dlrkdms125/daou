import smtplib
from email.mime.text import MIMEText
from .models import create_access_token


def send_access_mail(user: str, to_email: str):
    # 1. 토큰 기반 접근 URL 생성
    url = create_access_token(user)

    # 2. 메일 본문 작성
    subject = f"{user} 접속 알림"
    body = f"{user} 님의 데이터는 아래 링크에서 확인할 수 있습니다:\n\n{url}"

    # 3. 메일 전송 설정
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender = "somethingisnothing125@gmail.com"
    password = "qars ckgj rvbm rkng"   # ⚠️ Gmail 앱 비밀번호 필요

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    # 4. 메일 전송
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)

    return True

