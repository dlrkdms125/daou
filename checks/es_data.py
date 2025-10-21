import time
import requests
import datetime

ES_URL = "http://elasticsearch:9200/check/_doc"

def feed():
    while True:
        # doc이라는 json문서를 만듬
        doc = {
            "@timestamp": datetime.datetime.utcnow().isoformat(), # 현재시간 지정
            "message": "test log",
            "value": datetime.datetime.now().strftime("%H:%M:%S")
        }
        r = requests.post(f"{ES_URL}?refresh=wait_for", json=doc) # 엘라스틱 서치에 doc을 전송, es가 색인 후 검색 가능한 상태로 refresh될때까지 기다렸다가 응답을 반환
        print("Inserted into ES:", r.json())
        time.sleep(3600)  # 1시간 주기
