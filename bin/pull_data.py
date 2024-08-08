import requests
import json
import re
import configparser
import unicodedata
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()

config = configparser.ConfigParser()
config.read("config/connection.ini")
ENDPOINT = config["SPLUNK"]["endpoint"]
SPLUNK_TOKEN = config["SPLUNK"]["token"]



def make_safe_filename(search_name):
    # Normalize the string to NFKD form, which separates characters and their diacritics
    normalized_name = unicodedata.normalize("NFKD", search_name)

    # Encode to ASCII bytes, ignoring characters that can't be represented in ASCII
    ascii_encoded_name = normalized_name.encode("ASCII", "ignore")

    # Decode back to a string
    ascii_name = ascii_encoded_name.decode("ASCII")

    # Replace spaces with underscores
    safe_name = re.sub(r"\s+", "_", ascii_name)

    # Remove any remaining unsafe characters
    safe_name = re.sub(r"[^A-Za-z0-9_\-\.]", "", safe_name)

    # Ensure the filename is not empty
    if not safe_name:
        safe_name = "default_filename"

    return safe_name


def get_data():
    url = f"{ENDPOINT}/services/saved/searches?output_mode=json&count=0"

    payload = {}
    headers = {"Authorization": f"Bearer {SPLUNK_TOKEN}"}

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)

    return response.json()


if __name__ == "__main__":

    output_dir = ROOT / "raw_data"
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    data = get_data()

    searches = data["entry"]

    for search in searches:
        filename = make_safe_filename(search["name"]) + ".json"
        out_file = output_dir / filename

        with open(out_file, "w") as f:
            json.dump(search, f, indent=4)
