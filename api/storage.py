import os
import json
from askCO import Scroll

record_file = "api/static/storedrecords.json"

config = {
    "quiet": True,
    "sleep": 0.1,
    "api_key": os.environ.get("TPAK_RANDOM"),
    "timeout": 5,
    "attempts": 3,
    "query": "*",
    "fields":"pid,id,title,production,evidenceFor,identification,hasRepresentation,_meta",
    "max_records": 1000
}


def get_records():
    # Find out how many records you need to page through
    refresh_storage()
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
        save_records(scroll.records)
    else:
        print("No API key!")


def refresh_storage():
    if os.path.exists(record_file):
        os.remove(record_file)
        print("Previous record file deleted.")


def save_records(records):
    # Write result set to the storage file
    with open(record_file, "w+") as outfile:
        json.dump(records, outfile)
        print("Records saved to file.")


def load_record_file():
    # Load the saved records for the view
    try:
        with open(record_file) as openfile:
            memo = json.load(openfile)
            # print("Load data: ", [record["pid"] for record in memo])
            return memo
    except IOError:
        return False
