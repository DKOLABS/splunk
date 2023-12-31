import argparse
import keyring
import requests
import sys
import time
import math
import logging
import traceback
import pandas as pd
from pathlib import Path

BATCH_SIZE = 1000

requests.packages.urllib3.disable_warnings()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File Logger
file_handler = logging.FileHandler("SplunkUpload.log")
file_handler.setLevel(logging.INFO)

# Console Logger
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)


# Logging Format
file_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | ln: %(lineno)d | %(message)s"
)
console_formatter = logging.Formatter("%(message)s")
file_handler.setFormatter(file_formatter)
console_handler.setFormatter(console_formatter)

# add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("-----Start of Script-----")


def timer(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Start of function: {func.__name__}")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"End of function: {func.__name__}")
        logger.info(
            f"Time taken by {func.__name__} function: {end_time - start_time} seconds"
        )
        return result

    return wrapper


def end_script(code):
    logger.info("-----End of Script-----")
    sys.exit(code)


class DataShipper:
    def __init__(self, splunk_endpoint, hec_token) -> None:
        self.splunk_endpoint = splunk_endpoint
        self.headers = {
            "Authorization": f"Splunk {hec_token}",
            "Content-Type": "application/json",
        }

    def send_batch(self, batch, parms):
        # This is an attempt to fix the error "Out of range float values are not JSON compliant"
        batch = [
            {
                k: str(v) if isinstance(v, float) and not math.isfinite(v) else v
                for k, v in record.items()
            }
            for record in batch
        ]

        payload = {
            "event": batch,
            "host": parms["host"],
            "source": parms["source"],
            "sourcetype": "_json",
        }

        try:
            logger.info(f"Attempting to send {len(batch)} events to Splunk")
            response = requests.post(
                self.splunk_endpoint,
                headers=self.headers,
                json=payload,
                verify=parms["verify"],
            )
            logger.info(f"Received status code of: {response.status_code}")
        except requests.exceptions.SSLError as e:
            logger.error(e)
            logger.error(
                'If you would like to bypass this error, supply the command line argument "-k"'
            )
            end_script(0)
        except Exception as e:
            logger.error(f"An error of type {type(e).__name__} has occurred: {e}")
            logger.error(traceback.format_exc())

        if response.status_code != 200:
            logger.error(f"Failed to send event: {response.text}")

    # Send CSV data to Splunk
    @timer
    def send_csv_data(self, file_path, parms):
        try:
            for chunk in pd.read_csv(file_path, chunksize=BATCH_SIZE):
                self.send_batch(chunk.to_dict(orient="records"), parms)
        except pd.errors.ParserError as e:
            logging.error(f"Failed to parse CSV file: {e}")
            end_script(0)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            end_script(0)

    # Send JSON data to Splunk
    @timer
    def send_ndjson_data(self, file, parms):
        try:
            for chunk in pd.read_json(file, lines=True, chunksize=BATCH_SIZE):
                self.send_batch(chunk.to_dict(orient="records"), parms)
        except ValueError as e:
            logging.error(f"Failed to parse JSON file: {e}")
            end_script(0)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            end_script(0)


def validate_file(file):
    logger.info(f"Validating file: {file}")
    # Check if file exists
    if not file.is_file():
        return (False, f"File not found: {file}")

    # Determine if file type is supported
    if file.suffix == ".csv":
        logger.info("File type is CSV")
        return (True, "csv")
    elif file.suffix == ".json" or file.suffix == ".ndjson":
        logger.info("File type is NDJSON")
        return (True, "json")
    else:
        return (False, f'File type "{file.suffix}" not supported')


def get_hec_token():
    # Retrieve HEC token securely using keyring
    hec_token = keyring.get_password("splunk", "hec")
    if not hec_token:
        logger.error(
            'HEC token not found. Please set it by running "keyring set splunk hec".'
        )
        end_script(0)
    return hec_token


def get_splunk_server():
    # Retrieve HEC token securely using keyring
    splunk_server = keyring.get_password("splunk", "server")
    if not splunk_server:
        logger.error(
            'Splunk server not found. Please set it by running "keyring set splunk server".'
        )
        end_script(0)
    return splunk_server


if __name__ == "__main__":
    # Collect Arguments
    parser = argparse.ArgumentParser(
        description="Upload a CSV or NDJSON file to Splunk using HEC."
    )
    parser.add_argument(
        "--file", "-f", required=True, help="Path to the file to upload"
    )
    parser.add_argument("--host", "-n", required=True, help="Hostname")
    parser.add_argument("--source", "-s", required=True, help="Case ID")
    parser.add_argument("-k", action="store_false", help="Bypass TLS verification")
    parser.add_argument(
        "--sourcetype",
        "-t",
        required=False,
        help="Sourcetype - default is _json",
        default="_json",
    )

    args = parser.parse_args()

    # Validate the file exists and is a supported type
    file = Path(args.file)
    results = validate_file(file)
    if not results[0]:
        logger.error(results[1])
        end_script(0)

    file_type = results[1]

    # Collect the Splunk Endpoint and the HEC Token
    logger.info("Collecting HEC token from keyring")
    hec_token = get_hec_token()
    logger.info("Collecting Splunk endpoint token from keyring")
    splunk_server = get_splunk_server()

    # Setup parameters
    parameters = {"host": args.host, "source": args.source, "verify": args.k}

    shipper = DataShipper(splunk_endpoint=splunk_server, hec_token=hec_token)

    if file_type == "csv":
        shipper.send_csv_data(file, parameters)
    elif file_type == "json":
        shipper.send_ndjson_data(file, parameters)

end_script(0)
