import os
import random
from flask import Flask, render_template, session, redirect, url_for, request, g
from api import auth, harvester

config = {
    "quiet": True,
    "sleep": 0.1,
    "api_key": os.environ.get("TPAK_RANDOM"),
    "timeout": 5,
    "attempts": 3,
    "query": "*",
    "scroll_fields": "id",
    "max_records": -1,
    "record_data": None
}
stored_records = "api/static/data/records_file.txt"


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("TP_RANDOM_SECRET_KEY")
        # SECRET_KEY="dev"
    )

    app.register_blueprint(auth.bp)

    if not os.path.exists(stored_records):
        harvester.get_records(config, stored_records)

    try:
        irns = []
        with open(stored_records, "r", encoding="utf-8") as infile:
            data = infile.readlines()
            for irn in data:
                try:
                    irn.strip()
                    irn = int(irn)
                    irns.append(irn)
                except TypeError:
                    continue
            print("Loading {} records".format(len(irns)))
            config["record_data"] = irns

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
                return render_template("display.html",
                                       record=record,
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
            random_irn = random.choice(g.records)
            print("Selected {}".format(random_irn))

            record_data = harvester.request_record(config, random_irn)

            return record_data, record_count
        else:
            return False

    @app.route('/reload')
    def reload():
        return redirect(url_for("home"))

    return app


if __name__ == "__main__":
    create_app()
