import os

import requests

from .rdh_dl import (
    get_file,
    get_list
)

baseurl = "https://data.redistrictingdatahub.org/web_ready_stage"

pl_shp_path = "%2FPL2020%2Fshp%2F"

pl_files = {
    "block": "{st}_pl{dec_yyyy}_b.zip",
    "vtd": "{st}_pl{dec_yyyy}_vtd.zip",
    "tract": "{st}_pl{dec_yyyy}_t.zip",
    "county": "{st}_pl{dec_yyyy}_cnty.zip",
    "place": "{st}_pl{dec_yyyy}_place.zip",
    "aiannh": "{st}_pl{dec_yyyy}_aiannh.zip",
}

cvap_csv_path = "%2FCVAP%2Fcsv%2F2020_b_csv%2F"

cvap_files = {
    "block": "{st}_cvap_{acs_yyyy}_{dec_yyyy}_b.zip",
    "tract": "{st}_cvap_{acs_yyyy}_t.zip",
    "county": "{st}_cvap_{acs_yyyy}_cnty.zip",
    "place": "{st}_cvap_{acs_yyyy}_place.zip",
}


def download_files(dest_path, state, dec_yyyy, acs_yyyy):
    files = get_list(state)
    if not files:
        return False

    username = os.environ['username']
    password = os.environ['password']

    params = {
        "username": username,
        "password": password,
        "datasetid": "26202"
    }

    for _, file in pl_files.items():
        r = requests.get(
            f"{baseurl}{pl_shp_path}{file.format(st=state, dec_yyyy=dec_yyyy, acs_yyyy=acs_yyyy)}",
            params,
            allow_redirects=True
        )

        with open(dest_path / file, "w+") as f:
            f.write(r.content)

    for _, file in cvap_files.items():
        r = requests.get(
            f"{baseurl}{cvap_csv_path}{file.format(st=state, dec_yyyy=dec_yyyy, acs_yyyy=acs_yyyy)}",
            params,
            allow_redirects=True
        )

        with open(dest_path / file, "w+") as f:
            f.write(r.content)
