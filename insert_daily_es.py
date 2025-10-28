from datetime import datetime, timezone, timedelta
from elasticsearch import Elasticsearch, helpers

def insert_daily_logs():
    es = Elasticsearch("http://localhost:9200")
    today = (datetime.now(timezone.utc) - timedelta(days=1)).date()

    base_doc = {
        "server": "app-1",
        "user": "kaeunlee",
        "switch_su": "-",
        "sftp_file": "C:\\Users\\daou\\Desktop\\전산실 HW",
        "reason": "window",
        "appeal_done": False,  
        "status": "new",
    }

    times = ["03:00:00", "03:10:00", "03:20:00"]
    items = ["vdi","ssh"]
    actions = []

    for i, time_str in enumerate(times):
        for item in items:
            ip_suffix = 101 + i
            timestamp = f"{today}T{time_str}Z"

            doc = {
                **base_doc,
                "item": item,
                "date": str(today),
                "time": time_str,
                "ip": f"192.168.0.{ip_suffix}",
                "@timestamp": timestamp
            }

        actions.append({
            "_index": "checks_checkrecord",
            "_source": doc
        })

    helpers.bulk(es, actions)
    print(f"[{today}] inserted {len(actions)} docs → success")

if __name__ == "__main__":
    insert_daily_logs()
