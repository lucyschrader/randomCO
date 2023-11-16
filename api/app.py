import os
import random
from flask import Flask, render_template, session, redirect, url_for, request, g
from askCO import Scroll
from api import auth

config = {
    "quiet": True,
    "sleep": 0.1,
    "api_key": os.environ.get("TPAK_RANDOM"),
    "timeout": 5,
    "attempts": 3,
    "query": "*",
    "fields": "pid,id,title,production,evidenceFor,identification,hasRepresentation,_meta",
    "max_records": -1,
    "record_data": None
}

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.environ.get("TP_RANDOM_SECRET_KEY")
)

app.register_blueprint(auth.bp)


@app.route('/')
@auth.auth_required
def home():
    check_for_records()
    if not g.record_data:
        return render_template("startup.html")
    else:
        record, record_count = choose_random_record()
        if record:
            image_url = record["hasRepresentation"][0]["previewUrl"]
            iiif_url = record["hasRepresentation"][0]["iiifUrl"]

            record_metadata = extract_metadata(record)

            return render_template("display.html",
                                   record=record,
                                   image_url=image_url,
                                   iiif_url=iiif_url,
                                   record_metadata=record_metadata,
                                   record_count=record_count)

        else:
            return render_template("restart.html")


def check_for_records():
    record_data = config.get("record_data")
    if not record_data:
        g.record_data = None
    else:
        g.record_data = record_data


def choose_random_record():
    record_count = len(g.record_data)
    if record_count > 0:
        random_record = random.choice(g.record_data)
        print("Selected {}".format(random_record["pid"]))

        return random_record, record_count
    else:
        return False


def extract_metadata(record):
    record_metadata = {}

    record_metadata["rights"] = record["hasRepresentation"][0]["rights"]["title"]

    if record.get("production"):
        makers = []
        for prod in record["production"]:
            # Add any creators
            if prod.get("contributor"):
                maker = prod["contributor"].get("title")
                if maker:
                    makers.append(maker)

            # Add one creation location
            if not record_metadata.get("place_created"):
                if prod.get("spatial"):
                    record_metadata["place_created"] = prod["spatial"]["title"]

            # Add one creation date
            if not record_metadata.get("date_created"):
                if prod.get("createdDate"):
                    record_metadata["date_created"] = prod["createdDate"]

        if len(makers) > 0:
            record_metadata["makers"] = ", ".join(makers)

    if record.get("evidenceFor"):
        # Add any collectors
        collectors = []
        if record["evidenceFor"].get("atEvent"):
            collector_details = record["evidenceFor"]["atEvent"].get("recordedBy")
            if collector_details:
                for collector in collector_details:
                    collector_name = collector.get("title")
                    if collector_name:
                        collectors.append(collector_name)

        if len(collectors) > 0:
            record_metadata["collectors"] = ", ".join(collectors)

    if record.get("identification"):
        # Add identification details
        ids = []
        for identification in record["identification"]:
            # Add taxon and name of identifier
            id_taxon = identification["toTaxon"]["scientificName"]
            if identification.get("identifiedBy"):
                id_agent = identification["identifiedBy"]["title"]
            else:
                id_agent = "unknown"
            if id_taxon and id_agent:
                ids.append({"taxon": id_taxon, "agent": id_agent})

            if not record_metadata.get("vernacular_name"):
                vernacular = []
                common_names = identification.get("toTaxon").get("vernacularName")
                if common_names:
                    for name in common_names:
                        vernacular.append(name["title"])

                record_metadata["vernacular_name"] = vernacular

        if len(ids) > 0:
            record_metadata["identifications"] = ids

    return record_metadata


@app.route('/reload')
def reload():
    return redirect(url_for("home"))


@app.route('/harvest')
def harvest_records():
    record_data = get_records()
    if record_data:
        return {"records": "success"}
    else:
        print("Error getting records.")
        return {"records": "failure"}


def get_records():
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
            config["record_data"] = scroll.records
            return True
        else:
            return scroll.error_message, scroll.status_code
    else:
        print("No API key!")
        return None


if __name__ == '__main__':
    app.run()
