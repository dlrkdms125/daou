from elasticsearch import Elasticsearch
from django.conf import settings
from .models import CheckRecord
from django.utils import timezone
from datetime import datetime, timedelta, timezone

def save_es_doc_to_pg(es_doc): # 엘라스틱 서치에서 가져온 JSON문서를 CheckRecord객체로 변환해서 sqlite에 저장
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
        appeal_done=es_doc.get("appeal_done"), 
        status=es_doc.get("status") 
    )
    # record.save()는 orm을 통해 db.sqlite3 파일에 insert 쿼리를 날림
    record.save() 
KST = timezone(timedelta(hours=9))
def fetch_from_es(): # 엘라스틱 서치에서 최신 데이터를 가져와서 SQLITE에 저장하는 역할(전날에 새롭게 es에 추가된 데이터만 SQLITE에 저장)
    es = Elasticsearch(settings.ES_HOST)

    # 전날 날짜 계산
    yesterday = (datetime.now(KST) - timedelta(days=1)).date()

    start1 = f"{yesterday}T00:00:00"
    end1   = f"{yesterday}T05:59:59"

    start2 = f"{yesterday}T21:00:00"
    end2   = f"{yesterday}T23:59:59"

    # Elasticsearch 쿼리 (bool + should → OR 조건)
    query = {
        "query": {
            "bool": {
                "should": [
                    {"range": {"@timestamp": {"gte": start1, "lte": end1, "time_zone": "+00:00"}}},
                    {"range": {"@timestamp": {"gte": start2, "lte": end2, "time_zone": "+00:00"}}}
                ],
                "minimum_should_match": 1,
                "must_not": [
                    {"term":{"item.keyword":"vdi"}}
                ]
            }
        },
        "sort": [{"@timestamp": "asc"}],   # 시간순 정렬 (오래된 것부터)
        "size": 10000                      
    }

    res = es.search(index=settings.ES_INDEX, body=query)

    for hit in res["hits"]["hits"]: # 문서들의 리스트를 돌면서
        es_doc = hit["_source"] # 실제 저장된 문서의 데이터를 es_dos에 저장함
        save_es_doc_to_pg(es_doc) # 문서를 sqlite에 저장함
 
    print(f"Fetched {len(res['hits']['hits'])} docs")


def delete_old_records():
    now = timezone.now() 
    threshold = now - timedelta(week=4)
    deleted_count = 0

    for record in CheckRecord.objects.all():
        record_datetime = datetime.combine(record.date, record.time)

        if timezone.is_naive(record_datetime):
            record_datetime = timezone.make_aware(record_datetime, timezone.get_current_timezone())

        if record_datetime < threshold:
            record.delete()
            deleted_count += 1

    print(f"[LOG] {deleted_count} records deleted (before {threshold})")