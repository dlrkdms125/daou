import time
import requests
import datetime

ES_URL = "http://elasticsearch:9200/check/_doc"

def feed():
    while True:
        doc = {
            "@timestamp": datetime.datetime.utcnow().isoformat(),
            "message": "test log",
            "value": datetime.datetime.now().strftime("%H:%M:%S")
        }
        r = requests.post(f"{ES_URL}?refresh=wait_for", json=doc)
        print("Inserted into ES:", r.json())
        time.sleep(10)  # 10초 주기
