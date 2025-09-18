from elasticsearch import Elasticsearch
from django.conf import settings
from .models import CheckRecord
from datetime import datetime, timedelta

def save_es_doc_to_pg(es_doc): # 엘라스틱 서치에서 가져온 JSON문서를 CheckRecord객체로 변환해서 db에 저장
    record = CheckRecord(
        date=es_doc["@timestamp"].split("T")[0], # 날짜
        time=es_doc["@timestamp"].split("T")[1][:8], # 시각
        item=es_doc.get("item", ""),
        server=es_doc.get("server", ""),
        user=es_doc.get("user", ""),
        ip=es_doc.get("ip", ""),
        switch_su=es_doc.get("switch_su", ""),
        sftp_file=es_doc.get("sftp_file", ""),
        reason=es_doc.get("reason", ""),
        appeal_done=es_doc.get("appeal_done", False), # 없으면 False
        status=es_doc.get("status", "new") # 없으면 new
    )
    record.save()

def fetch_from_es(): # 엘라스틱 서치에서 최신 데이터를 가져와서 postgresql에 저장하는 역할(전날에 새롭게 es에 추가된 데이터만 postgresql에 저장)
    es = Elasticsearch(settings.ES_HOST)

    # 전날 날짜 계산
    yesterday = datetime.utcnow().date() - timedelta(days=1)

    start1 = f"{yesterday}T00:00:00"
    end1   = f"{yesterday}T05:59:59"

    start2 = f"{yesterday}T21:00:00"
    end2   = f"{yesterday}T23:59:59"

    # Elasticsearch 쿼리 (bool + should → OR 조건)
    query = {
        "query": {
            "bool": {
                "should": [
                    {"range": {"@timestamp": {"gte": start1, "lte": end1}}},
                    {"range": {"@timestamp": {"gte": start2, "lte": end2}}}
                ],
                "minimum_should_match": 1
            }
        },
        "sort": [{"@timestamp": "asc"}],   # 시간순 정렬 (오래된 것부터)
        "size": 10000                      # 충분히 크게 설정 (필요 시 scroll 사용)
    }

    res = es.search(index=settings.ES_INDEX, body=query)

    for hit in res["hits"]["hits"]:
        es_doc = hit["_source"]
        save_es_doc_to_pg(es_doc)

    print(f"Fetched {len(res['hits']['hits'])} docs")