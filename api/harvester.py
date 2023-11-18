from askCO import Scroll, Resource


def get_records(config, filename):
    if config.get("api_key"):
        scroll = Scroll(quiet=config.get("quiet"),
                        sleep=config.get("sleep"),
                        api_key=config.get("api_key"),
                        query=config.get("query"),
                        timeout=config.get("timeout"),
                        attempts=config.get("attempts"),
                        endpoint="object",
                        fields=config.get("scroll_fields"),
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
    irns = []
    for record in records:
        irns.append(record["id"])

    with open(filename, "w+", encoding="utf-8") as outfile:
        outfile.writelines("\n".join([str(irn) for irn in irns]))


def request_record(config, irn):
    if config.get("api_key"):
        requested_record = Resource(quiet=config.get("quiet"),
                                    sleep=config.get("sleep"),
                                    api_key=config.get("api_key"),
                                    timeout=config.get("timeout"),
                                    attempts=config.get("attempts"),
                                    irn=irn,
                                    endpoint="object")
        requested_record.send_query()
        if not requested_record.error_message:
            record_data = requested_record.response_text
            return extract_metadata(record_data)


def extract_metadata(record):
    irn = record["id"]
    pid = record["pid"]
    title = record.get("title")
    image_preview, image_iiif, rights = get_images(record["hasRepresentation"][0])
    creator, place_created, date_created = get_production(record.get("production"))
    collector, place_collected, date_collected = get_event(record.get("evidenceFor"))
    identifier, date_identified, scientific_name, vernacular_name = get_identification(record.get("identification"))

    return {"irn": irn,
            "pid": pid,
            "title": title,
            "imagePreview": image_preview,
            "imageIiif": image_iiif,
            "rights": rights,
            "creator": creator,
            "placeCreated": place_created,
            "dateCreated": date_created,
            "collector": collector,
            "placeCollected": place_collected,
            "dateCollected": date_collected,
            "identifiedBy": identifier,
            "dateIdentified": date_identified,
            "scientificName": scientific_name,
            "vernacularName": vernacular_name
            }


def get_images(image_data):
    image_preview = image_data.get("previewUrl")
    image_iiif = image_data.get("iiifUrl")
    try:
        rights = image_data["rights"]["title"]
    except KeyError:
        rights = None
    return image_preview, image_iiif, rights


def get_production(prod_data):
    creator = None
    place_created = None
    date_created = None
    if prod_data:
        first_prod = prod_data[0]
        if first_prod.get("contributor"):
            creator = first_prod["contributor"].get("title")
        if first_prod.get("spatial"):
            place_created = first_prod["spatial"].get("title")
        date_created = first_prod.get("createdDate")

    return creator, place_created, date_created


def get_event(event_data):
    collectors = []
    place_collected = None
    date_collected = None
    if event_data:
        collector_data = event_data["atEvent"].get("recordedBy")
        if collector_data:
            for collector in collector_data:
                if collector.get("title"):
                    collectors.append(collector["title"])
        if event_data.get("atLocation"):
            location = event_data.get("atLocation")
            if location:
                place_collected = location.get("title")
        date_collected = event_data.get("eventDate")

    if len(collectors) > 0:
        collectors = ", ".join(collectors)
    else:
        collectors = None

    return collectors, place_collected, date_collected


def get_identification(id_data):
    identifier = None
    date_identified = None
    scientific_name = None
    vernacular_name = None
    if id_data:
        first_id = id_data[0]
        identifier_data = first_id.get("identifiedBy")
        if identifier_data:
            identifier = identifier_data.get("title")
        date_identified = first_id.get("dateIdentified")
        taxon_data = first_id.get("toTaxon")
        if taxon_data:
            scientific_name = taxon_data.get("scientificName")
            common_names = taxon_data.get("vernacularName")
            if common_names:
                vernacular_name = common_names[0].get("title")

    return identifier, date_identified, scientific_name, vernacular_name
