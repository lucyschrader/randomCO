import json
from askCO import Scroll


def get_records(config, filename):
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
        if not scroll.error_message:
            print("Saving records!")
            save_records_to_file(scroll.records, filename)
        else:
            print(scroll.error_message, scroll.status_code)
    else:
        print("No API key!")
        return None


def save_records_to_file(records, filename):
    with open(filename, "w+") as outfile:
        json.dump(records, outfile)

