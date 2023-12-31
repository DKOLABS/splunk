# Splunk Data Uploader

## Overview

This Python script facilitates the upload of CSV or NDJSON data to Splunk using the HTTP Event Collector (HEC). It supports bulk uploads with configurable batch sizes.

## Prerequisites

- Python 3.x
- Required external Python packages: `keyring`, `requests`, `pandas`

## Usage

```bash
python script.py --file <path/to/file> --host <hostname> --source <case_id> [-k] [--sourcetype <sourcetype>]
```

## Arguments
- `--file` (`-f`): Path to the file to upload (required).
- `--host` (`-n`): Hostname (required).
- `--source` (`-s`): Case ID (required).
- `-k`: Bypass TLS verification (optional).
- `--sourcetype` (`-t`): Sourcetype (Default is `_json`, optional).

## Installation
1. Install Python 3.x if not already installed.
2. Install required packages:

```bash
pip install argparse keyring requests pandas
```

## Configuration
1. Set up the Splunk server address using the following command:

```bash
keyring set splunk server
```

2. Set up the HEC token using the following command:

```bash
keyring set splunk hec
```

## Examples

1. Upload a CSV file with TLS verification:

```bash
python SplunkUploader.py --file data.csv --host DT01 --source 55555
```

2. Upload an NDJSON file without TLS verification:

```bash
python SplunkUploader.py --file data.ndjson --host DT01 --source 55555 -k
```

## Logging
The script generates a log file named `SplunkUpload.log` containing information and errors.
