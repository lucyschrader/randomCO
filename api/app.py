import os
import random
import json
from flask import Flask, render_template, session, redirect, url_for, request, g
from api import auth, harvester

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
stored_records = "api/static/data/records_file.json"


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        # SECRET_KEY=os.environ.get("TP_RANDOM_SECRET_KEY")
        SECRET_KEY="dev"
    )

    app.register_blueprint(auth.bp)

    if not os.path.exists(stored_records):
        harvester.get_records(config, stored_records)

    try:
        with open(stored_records, "r") as infile:
            data = json.load(infile)
            if data:
                config["record_data"] = data
    except IOError:
        # To do: Add a fallback that gets one page of results
        print("No stored records")

    @app.route('/')
    @auth.auth_required
    def home():
        check_for_records()
        if g.records:
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

        return render_template("restart.html")

    def check_for_records():
        load_data = config.get("record_data")
        if load_data:
            g.records = load_data
        else:
            g.records = None

    def choose_random_record():
        record_count = len(g.records)
        if record_count > 0:
            random_record = random.choice(g.records)
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

    return app


if __name__ == "__main__":
    create_app()
