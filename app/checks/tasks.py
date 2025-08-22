from elasticsearch import Elasticsearch
from django.conf import settings
from .models import CheckRecord

def save_es_doc_to_pg(es_doc):
    record = CheckRecord(
        date=es_doc["@timestamp"].split("T")[0],
        time=es_doc["@timestamp"].split("T")[1][:8],
        item=es_doc.get("item", ""),
        server=es_doc.get("server", ""),
        user=es_doc.get("user", ""),
        ip=es_doc.get("ip", ""),
        switch_su=es_doc.get("switch_su", ""),
        sftp_file=es_doc.get("sftp_file", ""),
        reason=es_doc.get("reason", ""),
        appeal_done=es_doc.get("appeal_done", False),
        status=es_doc.get("status", "new")
    )
    record.save()

def fetch_from_es():
    print("Fetching data from Elasticsearch...")
    es = Elasticsearch(settings.ES_HOST)

    res = es.search(
        index=settings.ES_INDEX,
        body={"query": {"match_all": {}}, "size": 10, "sort": [{"@timestamp": "desc"}]}
    )

    for hit in res["hits"]["hits"]:
        es_doc = hit["_source"]
        save_es_doc_to_pg(es_doc)

    print(f"Fetched {len(res['hits']['hits'])} docs")
