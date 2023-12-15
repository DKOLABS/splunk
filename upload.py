import requests
import csv
import argparse
import keyring


def get_hec_token():
    # Retrieve HEC token securely using keyring
    hec_token = keyring.get_password("splunk", "hec")
    if not hec_token:
        print('HEC token not found. Please set it by running "keyring set splunk hec".')
        exit(1)
    return hec_token


def get_splunk_server():
    # Retrieve HEC token securely using keyring
    splunk_server = keyring.get_password("splunk", "server")
    if not splunk_server:
        print(
            'Splunk server not found. Please set it by running "keyring set splunk server".'
        )
        exit(1)
    return splunk_server


def upload_csv_to_splunk(csv_file_path, splunk_server, hec_token, host, source):
    url = f"https://{splunk_server}:8088/services/collector/event"
    headers = {
        "Authorization": f"Splunk {hec_token}",
        "Content-Type": "application/json",
    }

    with open(csv_file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            payload = {"event": row, "host": host, "source": source}
            response = requests.post(url, headers=headers, json=payload, verify=False)

            if response.status_code != 200:
                print(f"Failed to send event: {response.text}")


def main():
    parser = argparse.ArgumentParser(
        description="Upload a CSV file to Splunk using HEC."
    )
    parser.add_argument(
        "--csv", "-c", required=True, help="Path to the CSV file to upload"
    )
    parser.add_argument("--host", "-n", required=True, help="Hostname")
    parser.add_argument("--source", "-s", required=True, help="Phantom continer ID")

    args = parser.parse_args()

    hec_token = get_hec_token()
    splunk_server = get_splunk_server()
    upload_csv_to_splunk(args.csv, splunk_server, hec_token, args.host, args.source)


if __name__ == "__main__":
    main()
