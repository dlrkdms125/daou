# checks/tasks.py
from django.conf import settings
from elasticsearch import Elasticsearch
from .models import CheckRecord
from datetime import datetime, date  # ← dt 대신 직접 씀

def fetch_from_es():
    es = Elasticsearch(settings.ES_HOST)
    # 여러 인덱스를 쉼표로 받도록: 예) "ssh,su"
    index = settings.ES_INDEX
    query = {
        "bool": {
            "should": [
                {"range": {"@timestamp": {"gte": "now-2h", "lte": "now"}}},
                {"range": {"datetime":   {"gte": "now-2h", "lte": "now"}}},
            ],
            "minimum_should_match": 1,
        }
    }

    res = es.search(index=index, query=query, size=1000)
    # 이미 _source만 추출해 두고
    sources = [h.get("_source", {}) for h in res.get("hits", {}).get("hits", [])]

    created = 0
    for src in sources:  # ← 여기서는 src가 곧 문서 본문
        now = datetime.now()
        CheckRecord.objects.create(
            date   = src.get("date") or date.today(),
            time   = src.get("time") or now.strftime("%H:%M:%S"),
            server = src.get("server", "unknown"),
            ip     = src.get("ip", ""),
            reason = src.get("reason", ""),
            # 필요하면 item/user/status 등 추가
        )
        created += 1
    return created
