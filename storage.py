import os
import json
from askCO import Search
from math import ceil

record_file = "storedrecords.json"

config = {
    "quiet": True,
    "sleep": 0.1,
    "api_key": os.environ.get("TPAK-RANDOM"),
    "timeout": 5,
    "attempts": 3,
    "query": "*",
    "fields":"id,title,production,evidenceFor,identification,hasRepresentation,_meta",
    "max_records": 4000
}


def get_records():
    # Find out how many records you need to page through
    if config.get("api_key"):
        count_search = Search(quiet=config.get("quiet"),
                              sleep=config.get("sleep"),
                              api_key=config.get("api_key"),
                              query=config.get("query"),
                              timeout=config.get("timeout"),
                              attempts=config.get("attempts"),
                              endpoint="object",
                              fields="id",
                              size=1)
        count_search.send_query()
        page_through_results(count_search.record_count)
    else:
        print("No API key!")


def page_through_results(record_count):
    # Split the result set up into pages of 1000
    if config.get("max_records") and (config.get("max_records") < record_count):
        record_count = config.get("max_records")
    page_count = ceil(record_count/1000)
    for i in range(page_count):
        retrieve_page(i)


def retrieve_page(page):
    # Get a page of 1000 records at a time
    start_int = page * 1000
    page_search = Search(quiet=config.get("quiet"),
                         sleep=config.get("sleep"),
                         api_key=config.get("api_key"),
                         query=config.get("query"),
                         timeout=config.get("timeout"),
                         attempts=config.get("attempts"),
                         endpoint="object",
                         fields="id,pid,title,production,evidenceFor,identification,hasRepresentation,_meta",
                         size=1000,
                         start=start_int)

    page_search.send_query()
    save_page_records(page_search.records)


def save_page_records(records):
    # Check the records and save the ones with images
    records_for_storage = [record for record in records if record.get("hasRepresentation")]

    if len(records_for_storage) > 0:
        write_to_file(records_for_storage)


def write_to_file(records):
    # Write a page of records to the storage file
    # Currently not working - can write but not read and combine
    if not os.path.exists(record_file):
        append_data = False
        outfile = open(record_file, "x")
        outfile.close()
        print("Storage file created")
    else:
        append_data = True

    with open(record_file, "r+") as outfile:
        if append_data:
            file_data = json.load(outfile)
            # print("Read data: ", [record["pid"] for record in file_data])
            records.extend(file_data)

        # print("Write data: ", [record["pid"] for record in records])
        outfile.seek(0)
        json.dump(records, outfile)


def load_record_file():
    # Load the saved records for the view
    try:
        with open(record_file) as openfile:
            memo = json.load(openfile)
            # print("Load data: ", [record["pid"] for record in memo])
            return memo
    except IOError:
        return False
