import os
from askCO import Scroll

record_data = None

config = {
    "quiet": True,
    "sleep": 0.1,
    "api_key": os.environ.get("TPAK_RANDOM"),
    "timeout": 5,
    "attempts": 3,
    "query": "*",
    "fields":"pid,id,title,production,evidenceFor,identification,hasRepresentation,_meta",
    "max_records": None
}

if os.environ.get("TP_RANDOM_MAX_RECORDS"):
    config["max_records"] = os.environ.get("TP_RANDOM_MAX_RECORDS")


def get_records():
    # Find out how many records you need to page through
    if config.get("api_key"):
        scroll = Scroll(quiet=config.get("quiet"),
                        sleep=config.get("sleep"),
                        api_key=config.get("api_key"),
                        query=config.get("query"),
                        timeout=config.get("timeout"),
                        attempts=config.get("attempts"),
                        endpoint="object",
                        fields=config.get("fields"),
                        exists="hasRepresentation",
                        size=1000,
                        duration=1,
                        max_records=config["max_records"])
        scroll.send_query()
        return scroll.records
    else:
        print("No API key!")
