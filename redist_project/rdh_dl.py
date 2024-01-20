# -*- coding: utf-8 -*-
"""Redistricting Project Generator

    Create GeoPackage database with standard set of tables with 
    standardized field names

        begin                : 2023-08-14
        copyright            : (C) 2023 by Cryptodira
        email                : stuart@cryptodira.org
        git sha              : $Format:%H$

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful, but   *
 *   WITHOUT ANY WARRANTY; without even the implied warranty of            *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          *
 *   GNU General Public License for more details. You should have          *
 *   received a copy of the GNU General Public License along with this     *
 *   program. If not, see <http://www.gnu.org/licenses/>.                  *
 *                                                                         *
 ***************************************************************************/
"""
import io
import os
import re
import urllib.parse

import requests

baseurl = 'https://redistrictingdatahub.org/wp-json/download/list'

username = os.environ['USERNAME']
password = os.environ['PASSWORD']

dl_url_regex = re.compile(
    r'https://redistrictingdatahub.org/wp-json/download/file/web_ready_stage([%a-zA-Z0-9_.]+)?username=YOURUSERNAME&password=YOURPASSWORD&datasetid=([0-9]+)'
)

pl_regex = re.compile(r'([a-z]{2})_pl(\d{4})_(b|vtd|cnty|aiannh|place|t)')

cvap_regex = re.compile(
    r'([a-z]{2})_cvap_(\d{4})_((?:(\d{4})_)?b|vtd|cnty|aiannh|place|t)')

l2_geog = {
    'Block': 'b',
    'VTD': 'vtd'
}
l2_regex = re.compile(r'([A-Z]{2})_L2_(\d{4})_(Block|VTD)Agg)')
l2_vr_date_regex = re.compile(r'l2_\d{4}blockagg_(\d{8})')


def process_entry(entry):
    url = entry['URL']
    _, path, datasetid = dl_url_regex.match(url)
    if f := pl_regex.match(entry['Filename']):
        entry['Type'] = "PL"
        entry['Year'] = f[2]
        entry['Geography'] = f[3]
    elif f := l2_regex(entry['Filename']):
        entry['Type'] = "Voter File"
        entry['Year'] = f[2]
        entry['Geography'] = l2_geog[f[3]]
        if d := l2_vr_date_regex.match(url):
            entry['VR Date'] = d[1]
    elif f := cvap_regex.match(entry['Filename']):
        entry['Type'] = "CVAP"
        entry['ACS Year'] = f[2]
        entry['Geography'] = f[3] if not f[4] else 'b'
        entry['Year'] = f[4]
    else:
        entry['Type'] = "Other"

    entry['Path'] = urllib.parse.unquote(path)
    entry['DatasetID'] = datasetid
    return entry


def get_list(state):
    params = {
        'username': username,
        'password': password,
        'format': 'json',
        'states': state
    }
    r = requests.get(baseurl, params=params)
    if r.status_code != 200:
        return None
    l: list[dict[str, any]] = r.json()
    for f in l:
        process_entry(f)
    return l


def get_file(entry):
    url: str = entry['URL']
    url.replace('YOURUSERNAME', username)
    url.replace('YOURPASSWORD', password)
    r = requests.get(url, allow_redirects=True)
    if r.status_code != 200:
        return None
    return io.BytesIO(r.content)
