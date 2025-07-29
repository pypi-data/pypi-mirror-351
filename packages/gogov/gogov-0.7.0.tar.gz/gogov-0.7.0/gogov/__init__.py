import argparse
import csv
from collections import OrderedDict
import geochatt
import json

import re
import requests
from time import sleep, time
from .topicinfo import get_topic_field_info

import flatmate


def inverse(d):
    return dict([(v, k) for k, v in d.items()])


# f123d=lstr456;...
def process_assignments(ln):
    return dict(
        [
            tuple(it.split("="))
            for it in ln.split(";")
            if "=" in it and it.split("=")[1].startswith("lstr")
        ]
    )


class Client:
    def __init__(self, email, password, site, city_id, wait=10, search_limit=None):
        if wait is None:
            wait = 10
        self.base = "https://api.govoutreach.com"
        self.site = site
        self.city_id = city_id
        self.wait = wait
        self.prevtime = None
        self.login(email, password)
        self.search_limit = search_limit

    def throttle(self):
        current = time()
        if isinstance(self.prevtime, float):
            wait_time = self.prevtime + self.wait - current
            if wait_time > 0:
                print("[gogov] sleeping " + str(wait_time) + " seconds")
                sleep(wait_time)
        self.prevtime = current

    def login(self, email, password):
        url = self.base + "/users/sessions"
        headers = {"Content-Type": "application/json", "X-Gogovapps-Site": self.site}
        self.throttle()
        r = requests.post(
            url, headers=headers, json={"email": email, "password": password}
        )
        data = r.json()
        self.token = data["token"]
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.expiry = data["expiry"]
        self.session_id = data["id"]
        return data

    def logout(self):
        print("[gogov] logging out")
        url = self.base + "/users/sessions"
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "X-Gogovapps-Site": self.site,
        }
        self.throttle()
        r = requests.delete(url, headers=headers)
        data = r.json()
        print("[gogov] logged out")

    def get_all_topic_info(self):
        url = self.base + "/crm/requests/all_topic_info"
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "X-Gogovapps-Site": self.site,
        }
        self.throttle()
        r = requests.get(url, headers=headers)
        data = r.json()
        return data

    # returns a mapping of classification_id to custom field name to label
    # like '57402' => 'pothole4' => 'Vehicle Damage'
    # every custom field name should be unique, too
    # but not every label is unique
    def get_custom_fields(self):
        topic_ids = [topic["id"] for topic in self.get_topics()["data"]]

        url = "https://user.govoutreach.com/chattanoogacitytn/script.php?t=empreq"
        r = requests.get(url)
        text = r.text

        # parse lstr0='Time Abandoned or Inoperable';
        lstr_to_value = dict(re.findall(r"(lstr\d+)='([^']*)';", text))

        default_fstr_to_lstr = process_assignments(
            re.search(r"([^\n]+);switch", text).group(1)
        )

        # parses cases
        cases = dict(
            re.findall(r"case (\d+):\n([^\n]+)\nbreak;", text, flags=re.MULTILINE)
        )

        # convert cases (fstr to lstr)
        cases = dict([(k, process_assignments(v.strip())) for k, v in cases.items()])

        # map display names
        field_to_fstr = dict(
            re.findall(r" ([A-Za-z\d_]+)Display\([^;]+(f[a-z\d]+)\);", text)
        )

        fstr_to_field = inverse(field_to_fstr)

        # build dictionary of { [classification_id]: { [custom field name]: label } }
        # because the id depends on the classification being used
        # a classification is like an id
        results = {}

        for topic_id in topic_ids:
            results[topic_id] = {}

            if topic_id in cases:
                # first iterate over case/topic's fstr to lstr
                for fstr, lstr in cases[topic_id].items():
                    customFieldName = fstr_to_field[fstr]
                    results[topic_id][customFieldName] = lstr_to_value[lstr]

            # go through and fill in defaults if not already filled
            for fstr, lstr in default_fstr_to_lstr.items():
                customFieldName = fstr_to_field[fstr]
                if customFieldName not in results[topic_id]:
                    results[topic_id][customFieldName] = lstr_to_value[lstr]

        # add topic_id=None representing default values
        results[None] = {}
        for fstr, lstr in default_fstr_to_lstr.items():
            customFieldName = fstr_to_field[fstr]
            if customFieldName not in results[None]:
                results[None][customFieldName] = lstr_to_value[lstr]

        return results

    def get_topics(self):
        url = self.base + "/core/crm/topics"
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "X-Gogovapps-Site": self.site,
        }
        self.throttle()
        r = requests.get(url, headers=headers)
        data = r.json()
        return data

    def search(self):
        url = self.base + "/core/crm/search"
        headers = {"Authorization": self.token, "X-Gogovapps-Site": self.site}

        searchAfter = []

        results = []

        for i in range(1_000_000):
            payload = {
                "cityId": self.city_id,
                "searchAfter": searchAfter,
                "size": 100,
                "sort": [
                    {"dateEntered": {"missing": "_last", "order": "desc"}},
                    {"_id": "desc"},
                ],
            }
            print("[gogov] url:", url)
            # print("[gogov] headers:", headers)
            print("[gogov] payload:", payload)
            self.throttle()
            r = requests.post(url, headers=headers, json=payload)
            self.prevtime = (
                time()
            )  # throttle based on time the request completed (not started)
            print(
                "[gogov] response:", r.text[:500], ("..." if len(r.text) > 1000 else "")
            )
            data = r.json()

            hits = data["hits"]["hits"]

            if len(hits) == 0:
                break

            searchAfter = hits[-1]["sort"]

            sources = [hit["_source"] for hit in hits]

            results += sources

            if self.search_limit is not None and len(results) >= self.search_limit:
                break

        if self.search_limit is not None:
            results = results[: self.search_limit]

        return results

    def export_requests(self, filepath=None, fh=None, custom_fields=None):
        topic_id_to_field_name_to_label = self.get_custom_fields()

        # all_topic_info = self.get_all_topic_info()

        # get list of all topic ids
        # all_topic_ids = [t['id'] for t in all_topic_info]

        # Make a "flat" dictionary of the topic IDs and their names to get classificationName
        topics = self.get_topics()
        topics_ids = {
            topic["id"]: topic["attributes"]["name"] for topic in topics["data"]
        }

        base_columns = OrderedDict(
            [
                ("caseId", "caseId"),
                ("displayId", "displayId"),
                ("caseType", "caseType"),
                ("classificationId", "classificationId"),
                ("classificationName", "N/A"),
                ("departmentId", "departmentId"),
                ("contactId", "contactId"),
                ("contact2Id", "contact2Id"),
                ("description", "description"),
                ("location", "location"),
                ("latitude", "locationPoint.lat"),
                ("longitude", "locationPoint.lon"),
                ("dateEntered", "dateEntered"),
                ("howEntered", "howEntered"),
                ("enteredById", "enteredById"),
                ("status", "status"),
                ("assignedToId", "assignedToId"),
                ("dateClosed", "dateClosed"),
                ("closedById", "closedById"),
                ("reasonClosed", "reasonClosed"),
                ("dateExpectClose", "dateExpectClose"),
                ("priority", "priority"),
                ("cecaseId", "cecaseId"),
                ("dateLastUpdated", "dateLastUpdated"),
                ("contact.firstName", "contact.firstName"),
                ("contact.lastName", "contact.lastName"),
                ("contact.phone", "contact.phone"),
            ]
        )

        custom_columns = OrderedDict([])

        all_results = []
        for page in range(1):
            results = self.search()

            for source in results:
                classificationId = source["classificationId"]

                if "customFields" in source and len(source["customFields"]) >= 1:
                    classification_custom_field_names = topic_id_to_field_name_to_label[
                        str(classificationId)
                    ]

                    # overwrite custom fields, converting from list of dictionaries to a simple dictionary
                    source["customFields"] = dict(
                        [
                            (
                                classification_custom_field_names[
                                    fld["customFieldName"]
                                ],
                                (
                                    fld.get("valueText")
                                    or fld.get("valueDatetime")
                                    or ""
                                ).strip(),
                            )
                            for fld in source["customFields"]
                            if fld.get("customFieldName")
                        ]
                    )

                    # add to custom fields
                    if custom_fields is None:
                        for name in source["customFields"].keys():
                            if "." not in name:
                                if name not in custom_columns:
                                    custom_columns[name] = ".".join(
                                        ["customFields", name]
                                    )
                else:
                    source["customFields"] = {}

                # just want the source part
                all_results.append(source)

        if custom_fields is not None:
            custom_columns = OrderedDict(
                [(fld, ".".join(["customFields", fld])) for fld in custom_fields]
            )

        columns = OrderedDict(list(base_columns.items()) + list(custom_columns.items()))

        # trim any column names with spaces in them
        columns = OrderedDict(
            [
                (k.strip(), v.strip() if isinstance(v, str) else v)
                for k, v in columns.items()
            ]
        )

        print("[gogov] columns:", columns)
        flattened_results = flatmate.flatten(
            all_results, columns=columns, clean=True, skip_empty_columns=False
        )

        for row in flattened_results:
            for key in row:
                value = row[key]
                if isinstance(value, str):
                    value = value.strip()
                row[key.strip()] = value
                if key != key.strip():
                    del row[key]

        # Add the classification name using the classification ID
        for result in flattened_results:
            result["classificationName"] = topics_ids[result["classificationId"]]

        f = fh or open(filepath, "w", newline="", encoding="utf-8")

        writer = csv.DictWriter(f, fieldnames=list(columns.keys()))
        writer.writeheader()
        writer.writerows(flattened_results)

        if fh is None:
            f.close()

    # topic_fields: Lists fields associated with each topic (minus loc., desc., etc.)
    # field_values: Lists acceptable inputs for each drop-down field (often "Yes", "No", or "Unknown")
    topic_fields, field_values = get_topic_field_info()

    # Function that submits a CRM request to the client's site using the GOGov API
    #   address, longitude, and latitude make up the "location" parameter for the request:
    #      - address is required
    #      - longitude and latitude will be determined automatically from address if not provided
    #   description is required; be sure to include any specific information the service team may need
    #   contact_id defaults to 0; this indicates an anonymous requester
    #   assigned_to_id defaults to 0; this indicates automatic routing to the assignee
    #   "fields" param contains all other fields: {"field1": value1, "field2": value2, ...}
    # See the GOGov API: https://documenter.getpostman.com/view/11428138/TVzLpgCK#69dfabaf-84b2-416f-92e0-2857e0702982
    def submit_request(
        self,
        topic_id,
        address,
        longitude=None,
        latitude=None,
        description=None,
        contact_id=0,
        assigned_to_id=0,
        fields=None,
    ):
        # Make a dict of all topic_id: topic_name and use it to validate the user's input for topic_id
        topics = self.get_topics()
        topic_ids = {
            topic["id"]: topic["attributes"]["name"] for topic in topics["data"]
        }
        if topic_id not in topic_ids:
            raise ValueError(f"Invalid input for topic_id: {topic_id}")

        # If the user did not input an address, raise a ValueError
        if address is None:
            raise ValueError("No value provided for address.")

        # Check if the user input longitude and latitude; if one or both is missing, use geochatt to find them
        if longitude is None or latitude is None:
            try:
                coordinates = geochatt.get_parcel_centroid(address)
            except Exception:
                exception_message = f"""
                    longitude and latitude could not be determined for address: {address} ;

                    check to make sure the address is in Hamilton County, and follows the
                    format [street number] [street name] [street suffix (e.g., "drive")] ;

                    or manually input values for both longitude and latitude to override automatic
                    determination.
                """
                raise Exception(exception_message)
            else:
                longitude = coordinates.x
                latitude = coordinates.y

        # Set up the location parameter in the GOGov request format
        location = {
            "data": {
                "shortAddress": address,
                "coordinates": {"longitude": longitude, "latitude": latitude},
            }
        }

        # Raise a ValueError if there is no description provided
        if description is None:
            raise ValueError("No value provided for description.")

        # # Make a single dict with {id}: {value} for each field dict in "fields" for input validation
        # input_fields = {field["id"]: field["value"] for field in fields}

        # A dictionary of {fieldname}: {display value} for checking if the user input the display values in fields
        custom_fields = self.get_custom_fields()[topic_id]

        # Get the name assoc. with topic_id and check if the input for "fields" is missing any required ones
        topic_name = topic_ids[topic_id].upper()
        # topic_name.upper()
        required_fields = self.topic_fields[topic_name]
        missing_fields = []
        for (
            required_field
        ) in required_fields:  # Either the fieldname or display value is valid
            required_display_val = custom_fields[required_field]
            if required_field not in fields:
                if (
                    required_display_val in fields
                ):  # Replace display values with fieldnames
                    for field in list(fields):
                        if field == required_display_val:
                            fields[required_field] = fields.pop(required_display_val)
                else:
                    missing_fields.append((required_field, required_display_val))
        if len(missing_fields) > 0:
            raise ValueError(
                f"Missing ({len(missing_fields)}) required fields: {missing_fields}"
            )

        # Validate the user's input for any fields that are answered with drop-down boxes
        for field in fields:
            if (
                field in self.field_values
                and fields[field] not in self.field_values[field]
            ):
                invalid_message = f"""
                    Invalid input value for {field}: {fields[field]} ; 
                    list of valid input values for {field}: {self.field_values[field]}
                """
                raise ValueError(invalid_message)

        # The URL for submitting the request
        url = "https://api.govoutreach.com/crm/requests"

        # Necessary headers
        headers = {
            "Authorization": self.access_token,
            "X-Gogovapps-Site": self.site,
            "Content-Type": "application/json",
        }

        # Format the user's input for fields to fit the GOGov specification
        submit_fields = []
        for field in fields:
            submit_field = {"id": field, "value": fields[field]}
            submit_fields.append(submit_field)

        # JSON-formatted dict
        data = {
            "data": {
                "attributes": {
                    "topic-id": topic_id,
                    "description": description,
                    "contact-id": contact_id,
                    "assigned-to-id": assigned_to_id,
                    "custom-fields": submit_fields,
                    "location": location,
                }
            }
        }

        self.throttle()
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        print(f"[gogov] response: {response.text}")


def main():
    parser = argparse.ArgumentParser(
        prog="gogov",
        description="High-Level API Client for GoGov",
    )
    parser.add_argument(
        "method",
        help='method to run, can be "export-requests"',
    )
    parser.add_argument(
        "outpath", help="output filepath of where to save downloaded CSV"
    )
    parser.add_argument(
        "--base",
        type=str,
        help='base url for the API, like "https://api.govoutreach.com"',
    )
    parser.add_argument("--city-id", type=str, help="city id")
    parser.add_argument(
        "--custom-fields",
        type=str,
        help="comma-separated list of custom fields to include",
    )
    parser.add_argument("--email", type=str, help="email")
    parser.add_argument("--password", type=str, help="password")
    parser.add_argument("--site", type=str, help="site")
    parser.add_argument("--wait", type=float, help="wait")
    parser.add_argument(
        "--search-limit",
        type=int,
        help="maximum number of requests when searching or exporting",
    )
    args = parser.parse_args()

    if args.method not in ["export-requests", "export_requests"]:
        raise Except("[gogov] invalid or missing method")

    client = Client(
        email=args.email,
        password=args.password,
        site=args.site,
        city_id=args.city_id,
        search_limit=args.search_limit,
        wait=args.wait,
    )

    if args.method in ["export-requests", "export_requests"]:
        custom_fields = args.custom_fields.split(",") if args.custom_fields else None
        client.export_requests(args.outpath, custom_fields=custom_fields)

    client.logout()


if __name__ == "__main__":
    main()
