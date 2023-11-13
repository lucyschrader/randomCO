import random
from flask import Flask, render_template, url_for
from storage import get_records, load_record_file

app = Flask(__name__)
get_records()


@app.route('/')
def home():
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


def choose_random_record():
    records = load_record_file()
    if len(records) > 0:
        random_record = random.choice(records)
        print("Selected {}".format(random_record["pid"]))

        record_count = len(records)

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
    # Check this is right
    return url_for("home")


if __name__ == '__main__':
    app.run()
