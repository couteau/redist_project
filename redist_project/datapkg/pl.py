"""QGIS Redistricting Project Plugin - import pl data

        begin                : 2024-01-24
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Cryptodira
        email                : stuart@cryptodira.org

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
import logging
import pathlib
import sqlite3
import zipfile
from collections.abc import Callable
from tempfile import mkdtemp
from typing import (
    Optional,
    Union
)

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import wkt

from .geography import geographies
from .gpkg import createGpkgTable
from .population import pop_fields
from .state import states
from .utils import (
    check_download,
    null_progress,
    partial_progress,
    spatialite_connect
)

URLS = {
    "2020": {
        "pl_data": "https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/{state}/{st}{year}.pl.zip",
        "shape": "https://www2.census.gov/geo/tiger/TIGER2020PL/STATE/{fips}_{state_caps}/{fips}/tl_{year}_{fips}_{geog}{yy}.zip"
    },
    "2010": {
        "pl_data": "https://www2.census.gov/census_{year}/01-Redistricting_File--PL_94-171/{state}/{st}{year}.pl.zip",
        "shape": "https://www2.census.gov/geo/pvs/tiger{year}st/{fips}_{state}/{fips}/tl_{year}_{fips}_{geog}{yy}.zip"
    }
}


def download_and_extract_pl(
        st: str,
        dec_year: str,
        dest: pathlib.Path,
        progress: Callable[[Union[int, float]], None] = None
):
    logging.info("Downloading %s PL 94-171 data", dec_year)
    pl_zip = check_download(
        URLS[dec_year]["pl_data"].format(
            st=st,
            year=dec_year,
            yy=dec_year[-2:],
            state=states[st].name.replace(' ', '_'),
            state_caps=states[st].name.upper().replace(' ', '_'),
            st_caps=st.upper(),
            fips=states[st].fips
        ),
        dest,
        progress
    )

    if pl_zip is None:
        return None

    pl_dest = dest / "pl_data"
    if pl_dest.exists():
        return pl_dest

    pl_dest.mkdir()
    with zipfile.ZipFile(pl_zip, "r") as z:
        z.extractall(pl_dest)

    return pl_dest


def download_shapefiles(
    st: str,
    dec_year: str,
    geogs: list[str],
    dest: pathlib.Path,
    progress: Callable[[Union[int, float]], None] = None
):
    for geog in geogs:
        logging.info("Downloading %s shapefiles", dec_year)
        check_download(
            URLS[dec_year]["shape"].format(
                st=st,
                year=dec_year,
                yy=dec_year[-2:],
                state=states[st].name.replace(' ', '_'),
                state_caps=states[st].name.upper().replace(' ', '_'),
                st_caps=st.upper(),
                fips=states[st].fips,
                geog=geographies[geog].shp
            ),
            dest,
            progress
        )

    return dest


header_dict: dict[str, dict[str, dict[str, type]]] = {
    "2020": {
        'Geoheader': {
            "FILEID": "string", "STUSAB": "string", "SUMLEV": "string", "GEOVAR": "string",
            "GEOCOMP": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "string",
            "GEOID": "string", "GEOCODE": "string", "REGION": "string", "DIVISION": "string",
            "STATE": "string", "STATENS": "string",
            "COUNTY": "string", "COUNTYCC": "string", "COUNTYNS": "string",
            "COUSUB": "string", "COUSUBCC": "string", "COUSUBNS": "string",
            "SUBMCD": "string", "SUBMCDCC": "string", "SUBMCDNS": "string",
            "ESTATE": "string", "ESTATECC": "string", "ESTATENS": "string",
            "CONCIT": "string", "CONCITCC": "string", "CONCITNS": "string",
            "PLACE": "string", "PLACECC": "string", "PLACENS": "string",
            "TRACT": "string", "BLKGRP": "string", "BLOCK": "string",
            "AIANHH": "string", "AIHHTLI": "string", "AIANHHFP": "string",
            "AIANHHCC": "string", "AIANHHNS": "string",
            "AITS": "string", "AITSFP": "string", "AITSCC": "string", "AITSNS": "string",
            "TTRACT": "string", "TBLKGRP": "string",
            "ANRC": "string", "ANRCCC": "string", "ANRCNS": "string",
            "CBSA": "string", "MEMI": "string", "CSA": "string", "METDIV": "string",
            "NECTA": "string", "NMEMI": "string", "CNECTA": "string", "NECTADIV": "string",
            "CBSAPCI": "string", "NECTAPCI": "string",
            "UA": "string", "UATYPE": "string", "UR": "string",
            "CD116": "string", "CD118": "string", "CD119": "string", "CD120": "string", "CD121": "string",
            "SLDU18": "string", "SLDU22": "string", "SLDU24": "string", "SLDU26": "string", "SLDU28": "string",
            "SLDL18": "string", "SLDL22": "string", "SLDL24": "string", "SLDL26": "string", "SLDL28": "string",
            "VTD": "string", "VTDI": "string", "ZCTA": "string",
            "SDELM": "string", "SDSEC": "string", "SDUNI": "string",
            "PUMA": "string", "AREALAND": "string", "AREAWATR": "string",
            "BASENAME": "string", "NAME": "string", "FUNCSTAT": "string", "GCUNI": "string",
            "POP100": "Int64", "HU100": "Int64", "INTPTLAT": "string", "INTPTLON": "string",
            "LSADC": "string", "PARTFLAG": "string", "UGA": "string"
        },
        '00001': {
            "FILEID": "string", "STUSAB": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "string",
            "P0010001": 'int', "P0010002": 'int', "P0010003": 'int', "P0010004": 'int', "P0010005": 'int',
            "P0010006": 'int', "P0010007": 'int', "P0010008": 'int', "P0010009": 'int', "P0010010": 'int',
            "P0010011": 'int', "P0010012": 'int', "P0010013": 'int', "P0010014": 'int', "P0010015": 'int',
            "P0010016": 'int', "P0010017": 'int', "P0010018": 'int', "P0010019": 'int', "P0010020": 'int',
            "P0010021": 'int', "P0010022": 'int', "P0010023": 'int', "P0010024": 'int', "P0010025": 'int',
            "P0010026": 'int', "P0010027": 'int', "P0010028": 'int', "P0010029": 'int', "P0010030": 'int',
            "P0010031": 'int', "P0010032": 'int', "P0010033": 'int', "P0010034": 'int', "P0010035": 'int',
            "P0010036": 'int', "P0010037": 'int', "P0010038": 'int', "P0010039": 'int', "P0010040": 'int',
            "P0010041": 'int', "P0010042": 'int', "P0010043": 'int', "P0010044": 'int', "P0010045": 'int',
            "P0010046": 'int', "P0010047": 'int', "P0010048": 'int', "P0010049": 'int', "P0010050": 'int',
            "P0010051": 'int', "P0010052": 'int', "P0010053": 'int', "P0010054": 'int', "P0010055": 'int',
            "P0010056": 'int', "P0010057": 'int', "P0010058": 'int', "P0010059": 'int', "P0010060": 'int',
            "P0010061": 'int', "P0010062": 'int', "P0010063": 'int', "P0010064": 'int', "P0010065": 'int',
            "P0010066": 'int', "P0010067": 'int', "P0010068": 'int', "P0010069": 'int', "P0010070": 'int',
            "P0010071": 'int', "P0020001": 'int', "P0020002": 'int', "P0020003": 'int', "P0020004": 'int',
            "P0020005": 'int', "P0020006": 'int', "P0020007": 'int', "P0020008": 'int', "P0020009": 'int',
            "P0020010": 'int', "P0020011": 'int', "P0020012": 'int', "P0020013": 'int', "P0020014": 'int',
            "P0020015": 'int', "P0020016": 'int', "P0020017": 'int', "P0020018": 'int', "P0020019": 'int',
            "P0020020": 'int', "P0020021": 'int', "P0020022": 'int', "P0020023": 'int', "P0020024": 'int',
            "P0020025": 'int', "P0020026": 'int', "P0020027": 'int', "P0020028": 'int', "P0020029": 'int',
            "P0020030": 'int', "P0020031": 'int', "P0020032": 'int', "P0020033": 'int', "P0020034": 'int',
            "P0020035": 'int', "P0020036": 'int', "P0020037": 'int', "P0020038": 'int', "P0020039": 'int',
            "P0020040": 'int', "P0020041": 'int', "P0020042": 'int', "P0020043": 'int', "P0020044": 'int',
            "P0020045": 'int', "P0020046": 'int', "P0020047": 'int', "P0020048": 'int', "P0020049": 'int',
            "P0020050": 'int', "P0020051": 'int', "P0020052": 'int', "P0020053": 'int', "P0020054": 'int',
            "P0020055": 'int', "P0020056": 'int', "P0020057": 'int', "P0020058": 'int', "P0020059": 'int',
            "P0020060": 'int', "P0020061": 'int', "P0020062": 'int', "P0020063": 'int', "P0020064": 'int',
            "P0020065": 'int', "P0020066": 'int', "P0020067": 'int', "P0020068": 'int', "P0020069": 'int',
            "P0020070": 'int', "P0020071": 'int', "P0020072": 'int', "P0020073": 'int'
        },
        '00002': {
            "FILEID": "string", "STUSAB": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "string",
            "P0030001": 'int', "P0030002": 'int', "P0030003": 'int', "P0030004": 'int', "P0030005": 'int',
            "P0030006": 'int', "P0030007": 'int', "P0030008": 'int', "P0030009": 'int', "P0030010": 'int',
            "P0030011": 'int', "P0030012": 'int', "P0030013": 'int', "P0030014": 'int', "P0030015": 'int',
            "P0030016": 'int', "P0030017": 'int', "P0030018": 'int', "P0030019": 'int', "P0030020": 'int',
            "P0030021": 'int', "P0030022": 'int', "P0030023": 'int', "P0030024": 'int', "P0030025": 'int',
            "P0030026": 'int', "P0030027": 'int', "P0030028": 'int', "P0030029": 'int', "P0030030": 'int',
            "P0030031": 'int', "P0030032": 'int', "P0030033": 'int', "P0030034": 'int', "P0030035": 'int',
            "P0030036": 'int', "P0030037": 'int', "P0030038": 'int', "P0030039": 'int', "P0030040": 'int',
            "P0030041": 'int', "P0030042": 'int', "P0030043": 'int', "P0030044": 'int', "P0030045": 'int',
            "P0030046": 'int', "P0030047": 'int', "P0030048": 'int', "P0030049": 'int', "P0030050": 'int',
            "P0030051": 'int', "P0030052": 'int', "P0030053": 'int', "P0030054": 'int', "P0030055": 'int',
            "P0030056": 'int', "P0030057": 'int', "P0030058": 'int', "P0030059": 'int', "P0030060": 'int',
            "P0030061": 'int', "P0030062": 'int', "P0030063": 'int', "P0030064": 'int', "P0030065": 'int',
            "P0030066": 'int', "P0030067": 'int', "P0030068": 'int', "P0030069": 'int', "P0030070": 'int',
            "P0030071": 'int', "P0040001": 'int', "P0040002": 'int', "P0040003": 'int', "P0040004": 'int',
            "P0040005": 'int', "P0040006": 'int', "P0040007": 'int', "P0040008": 'int', "P0040009": 'int',
            "P0040010": 'int', "P0040011": 'int', "P0040012": 'int', "P0040013": 'int', "P0040014": 'int',
            "P0040015": 'int', "P0040016": 'int', "P0040017": 'int', "P0040018": 'int', "P0040019": 'int',
            "P0040020": 'int', "P0040021": 'int', "P0040022": 'int', "P0040023": 'int', "P0040024": 'int',
            "P0040025": 'int', "P0040026": 'int', "P0040027": 'int', "P0040028": 'int', "P0040029": 'int',
            "P0040030": 'int', "P0040031": 'int', "P0040032": 'int', "P0040033": 'int', "P0040034": 'int',
            "P0040035": 'int', "P0040036": 'int', "P0040037": 'int', "P0040038": 'int', "P0040039": 'int',
            "P0040040": 'int', "P0040041": 'int', "P0040042": 'int', "P0040043": 'int', "P0040044": 'int',
            "P0040045": 'int', "P0040046": 'int', "P0040047": 'int', "P0040048": 'int', "P0040049": 'int',
            "P0040050": 'int', "P0040051": 'int', "P0040052": 'int', "P0040053": 'int', "P0040054": 'int',
            "P0040055": 'int', "P0040056": 'int', "P0040057": 'int', "P0040058": 'int', "P0040059": 'int',
            "P0040060": 'int', "P0040061": 'int', "P0040062": 'int', "P0040063": 'int', "P0040064": 'int',
            "P0040065": 'int', "P0040066": 'int', "P0040067": 'int', "P0040068": 'int', "P0040069": 'int',
            "P0040070": 'int', "P0040071": 'int', "P0040072": 'int', "P0040073": 'int',
            "H0010001": 'int', "H0010002": 'int', "H0010003": 'int'},
        '00003': {
            "FILEID": "string", "STUSAB": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "string",
            "P0050001": 'int', "P0050002": 'int', "P0050003": 'int', "P0050004": 'int', "P0050005": 'int',
            "P0050006": 'int', "P0050007": 'int', "P0050008": 'int', "P0050009": 'int', "P0050010": 'int'
        },
    },
    "2010": {
        'Geoheader': {
            "FILEID": "string", "STUSAB": "string", "SUMLEV": "string", "GEOCOMP": "string", "CHARITER": "string",
            "CIFSN": "string", "LOGRECNO": "string", "REGION": "string", "DIVISION": "string", "STATE": "string",
            "COUNTY": "string", "COUNTYCC": "string", "COUNTYSC": "string",
            "COUSUB": "string", "COUSUBCC": "string", "COUSUBSC": "string",
            "PLACE": "string", "PLACECC": "string", "PLACESC": "string",
            "TRACT": "string", "BLKGRP": "string", "BLOCK": "string",
            "IUC": "string", "CONCIT": "string", "CONCITCC": "string", "CONCITSC": "string",
            "AIANHH": "string", "AIANHHFP": "string", "AIANHHCC": "string", "AIHHTLI": "string",
            "AITSCE": "string", "AITS": "string", "AITSCC": "string", "TTRACT": "string", "TBLKGRP": "string",
            "ANRC": "string", "ANRCCC": "string", "CBSA": "string", "CBSASC": "string",
            "METDIV": "string", "CSA": "string",
            "NECTA": "string", "NECTASC": "string", "NECTADIV": "string", "CNECTA": "string",
            "CBSAPCI": "string", "NECTAPCI": "string",
            "UA": "string", "UASC": "string", "UATYPE": "string", "UR": "string",
            "CD": "string", "SLDU": "string", "SLDL": "string",
            "VTD": "string", "VTDI": "string", "RESERVE2": "string", "ZCTA5": "string",
            "SUBMCD": "string", "SUBMCDCC": "string", "SDELM": "string", "SDSEC": "string", "SDUNI": "string",
            "AREALAND": "string", "AREAWATR": "string", "NAME": "string", "FUNCSTAT": "string", "GCUNI": "string",
            "POP100": "string", "HU100": "string", "INTPTLAT": "string", "INTPTLON": "string",
            "LSADC": "string", "PARTFLAG": "string", "RESERVE3": "string", "UGA": "string",
            "STATENS": "string", "COUNTYNS": "string", "COUSUBNS": "string", "PLACENS": "string",
            "CONCITNS": "string", "AIANHHNS": "string", "AITSNS": "string", "ANRCNS": "string", "SUBMCDNS": "string",
            "CD113": "string", "CD114": "string", "CD115": "string",
            "SLDU2": "string", "SLDU3": "string", "SLDU4": "string",
            "SLDL2": "string", "SLDL3": "string", "SLDL4": "string",
            "AIANHHSC": "string", "CSASC": "string", "CNECTASC": "string", "MEMI": "string", "NMEMI": "string",
            "PUMA": "string", "RESERVED": "string"
        },
        '00001': {
            "FILEID": "string", "STUSAB": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "string",
            "P0010001": 'int', "P0010002": 'int', "P0010003": 'int', "P0010004": 'int', "P0010005": 'int',
            "P0010006": 'int', "P0010007": 'int', "P0010008": 'int', "P0010009": 'int', "P0010010": 'int',
            "P0010011": 'int', "P0010012": 'int', "P0010013": 'int', "P0010014": 'int', "P0010015": 'int',
            "P0010016": 'int', "P0010017": 'int', "P0010018": 'int', "P0010019": 'int', "P0010020": 'int',
            "P0010021": 'int', "P0010022": 'int', "P0010023": 'int', "P0010024": 'int', "P0010025": 'int',
            "P0010026": 'int', "P0010027": 'int', "P0010028": 'int', "P0010029": 'int', "P0010030": 'int',
            "P0010031": 'int', "P0010032": 'int', "P0010033": 'int', "P0010034": 'int', "P0010035": 'int',
            "P0010036": 'int', "P0010037": 'int', "P0010038": 'int', "P0010039": 'int', "P0010040": 'int',
            "P0010041": 'int', "P0010042": 'int', "P0010043": 'int', "P0010044": 'int', "P0010045": 'int',
            "P0010046": 'int', "P0010047": 'int', "P0010048": 'int', "P0010049": 'int', "P0010050": 'int',
            "P0010051": 'int', "P0010052": 'int', "P0010053": 'int', "P0010054": 'int', "P0010055": 'int',
            "P0010056": 'int', "P0010057": 'int', "P0010058": 'int', "P0010059": 'int', "P0010060": 'int',
            "P0010061": 'int', "P0010062": 'int', "P0010063": 'int', "P0010064": 'int', "P0010065": 'int',
            "P0010066": 'int', "P0010067": 'int', "P0010068": 'int', "P0010069": 'int', "P0010070": 'int',
            "P0010071": 'int', "P0020001": 'int', "P0020002": 'int', "P0020003": 'int', "P0020004": 'int',
            "P0020005": 'int', "P0020006": 'int', "P0020007": 'int', "P0020008": 'int', "P0020009": 'int',
            "P0020010": 'int', "P0020011": 'int', "P0020012": 'int', "P0020013": 'int', "P0020014": 'int',
            "P0020015": 'int', "P0020016": 'int', "P0020017": 'int', "P0020018": 'int', "P0020019": 'int',
            "P0020020": 'int', "P0020021": 'int', "P0020022": 'int', "P0020023": 'int', "P0020024": 'int',
            "P0020025": 'int', "P0020026": 'int', "P0020027": 'int', "P0020028": 'int', "P0020029": 'int',
            "P0020030": 'int', "P0020031": 'int', "P0020032": 'int', "P0020033": 'int', "P0020034": 'int',
            "P0020035": 'int', "P0020036": 'int', "P0020037": 'int', "P0020038": 'int', "P0020039": 'int',
            "P0020040": 'int', "P0020041": 'int', "P0020042": 'int', "P0020043": 'int', "P0020044": 'int',
            "P0020045": 'int', "P0020046": 'int', "P0020047": 'int', "P0020048": 'int', "P0020049": 'int',
            "P0020050": 'int', "P0020051": 'int', "P0020052": 'int', "P0020053": 'int', "P0020054": 'int',
            "P0020055": 'int', "P0020056": 'int', "P0020057": 'int', "P0020058": 'int', "P0020059": 'int',
            "P0020060": 'int', "P0020061": 'int', "P0020062": 'int', "P0020063": 'int', "P0020064": 'int',
            "P0020065": 'int', "P0020066": 'int', "P0020067": 'int', "P0020068": 'int', "P0020069": 'int',
            "P0020070": 'int', "P0020071": 'int', "P0020072": 'int', "P0020073": 'int'
        },
        '00002': {
            "FILEID": "string", "STUSAB": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "string",
            "P0030001": 'int', "P0030002": 'int', "P0030003": 'int', "P0030004": 'int', "P0030005": 'int',
            "P0030006": 'int', "P0030007": 'int', "P0030008": 'int', "P0030009": 'int', "P0030010": 'int',
            "P0030011": 'int', "P0030012": 'int', "P0030013": 'int', "P0030014": 'int', "P0030015": 'int',
            "P0030016": 'int', "P0030017": 'int', "P0030018": 'int', "P0030019": 'int', "P0030020": 'int',
            "P0030021": 'int', "P0030022": 'int', "P0030023": 'int', "P0030024": 'int', "P0030025": 'int',
            "P0030026": 'int', "P0030027": 'int', "P0030028": 'int', "P0030029": 'int', "P0030030": 'int',
            "P0030031": 'int', "P0030032": 'int', "P0030033": 'int', "P0030034": 'int', "P0030035": 'int',
            "P0030036": 'int', "P0030037": 'int', "P0030038": 'int', "P0030039": 'int', "P0030040": 'int',
            "P0030041": 'int', "P0030042": 'int', "P0030043": 'int', "P0030044": 'int', "P0030045": 'int',
            "P0030046": 'int', "P0030047": 'int', "P0030048": 'int', "P0030049": 'int', "P0030050": 'int',
            "P0030051": 'int', "P0030052": 'int', "P0030053": 'int', "P0030054": 'int', "P0030055": 'int',
            "P0030056": 'int', "P0030057": 'int', "P0030058": 'int', "P0030059": 'int', "P0030060": 'int',
            "P0030061": 'int', "P0030062": 'int', "P0030063": 'int', "P0030064": 'int', "P0030065": 'int',
            "P0030066": 'int', "P0030067": 'int', "P0030068": 'int', "P0030069": 'int', "P0030070": 'int',
            "P0030071": 'int', "P0040001": 'int', "P0040002": 'int', "P0040003": 'int', "P0040004": 'int',
            "P0040005": 'int', "P0040006": 'int', "P0040007": 'int', "P0040008": 'int', "P0040009": 'int',
            "P0040010": 'int', "P0040011": 'int', "P0040012": 'int', "P0040013": 'int', "P0040014": 'int',
            "P0040015": 'int', "P0040016": 'int', "P0040017": 'int', "P0040018": 'int', "P0040019": 'int',
            "P0040020": 'int', "P0040021": 'int', "P0040022": 'int', "P0040023": 'int', "P0040024": 'int',
            "P0040025": 'int', "P0040026": 'int', "P0040027": 'int', "P0040028": 'int', "P0040029": 'int',
            "P0040030": 'int', "P0040031": 'int', "P0040032": 'int', "P0040033": 'int', "P0040034": 'int',
            "P0040035": 'int', "P0040036": 'int', "P0040037": 'int', "P0040038": 'int', "P0040039": 'int',
            "P0040040": 'int', "P0040041": 'int', "P0040042": 'int', "P0040043": 'int', "P0040044": 'int',
            "P0040045": 'int', "P0040046": 'int', "P0040047": 'int', "P0040048": 'int', "P0040049": 'int',
            "P0040050": 'int', "P0040051": 'int', "P0040052": 'int', "P0040053": 'int', "P0040054": 'int',
            "P0040055": 'int', "P0040056": 'int', "P0040057": 'int', "P0040058": 'int', "P0040059": 'int',
            "P0040060": 'int', "P0040061": 'int', "P0040062": 'int', "P0040063": 'int', "P0040064": 'int',
            "P0040065": 'int', "P0040066": 'int', "P0040067": 'int', "P0040068": 'int', "P0040069": 'int',
            "P0040070": 'int', "P0040071": 'int', "P0040072": 'int', "P0040073": 'int', "H0010001": 'int',
            "H0010002": 'int', "H0010003": 'int'
        },
        '00003': {
            "FILEID": "string", "STUSAB": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "string",
            "P0050001": 'int', "P0050002": 'int', "P0050003": 'int', "P0050004": 'int', "P0050005": 'int',
            "P0050006": 'int', "P0050007": 'int', "P0050008": 'int', "P0050009": 'int', "P0050010": 'int'
        },
    }
}

field_widths_2010 = [
    6, 2, 3, 2, 3, 2, 7, 1, 1, 2, 3, 2, 2, 5, 2, 2, 5, 2, 2, 6, 1, 4, 2, 5, 2, 2, 4, 5, 2, 1, 3, 5,
    2, 6, 1, 5, 2, 5, 2, 5, 3, 5, 2, 5, 3, 1, 1, 5, 2, 1, 1, 2, 3, 3, 6, 1, 3, 5, 5, 2, 5, 5, 5,
    14, 14, 90, 1, 1, 9, 9, 11, 12, 2, 1, 6, 5, 8, 8, 8, 8, 8, 8, 8, 8, 8, 2, 2, 2, 3, 3, 3, 3, 3,
    3, 2, 2, 2, 1, 1, 5, 18
]


geoids = {
    "040": ["state"],
    "050": ["state", "county"],
    "060": ["state", "county", "cousub"],
    "067": ["state", "county", "submcd"],
    "140": ["state", "county", "tract"],
    "144": ["state", "county", "tract", "aianhh"],
    "150": ["state", "county", "tract", "blkgrp"],
    "154": ["state", "county", "tract", "blkgrp", "aianhh"],
    "155": ["state", "place", "county"],
    "158": ["state", "place", "county", "tract"],
    "160": ["state", "place"],
    "170": ["state", "concit"],
    "172": ["state", "concit", "place"],
    "230": ["state", "anrc"],
    "261": ["state", "aianhh", "county", "cousub"],
    "263": ["state", "aianhh", "county", "cousub", "place"],
    "280": ["state", "aianhh", "aihhtli"],
    "281": ["state", "aianhh", "aitsce"],
    "282": ["state", "aianhh", "county"],
    "283": ["state", "aianhh", "aihhtli"],
    "286": ["state", "aianhh", "aihhtli"],
    "320": ["state", "cbsa"],
    "340": ["state", "csa"],
    "341": ["state", "csa", "cbsa"],
    "360": ["state", "necta"],
    "700": ["state", "county", "vtd"],
    "750": ["state", "county", "tract", "block"],
    "860": ["zcta5"],
    "870": ["zcta5", "state"],
    "880": ["zcta5", "state", "county"]
}


def load_pl_data(
    st: str,
    dec_year,
    path: pathlib.Path,
    progress: Callable[[Union[int, float]], None] = null_progress
) -> pd.DataFrame:
    logging.info("Tabulating %s PL 94-171 data", dec_year)

    seg_files = list(path.glob(f"{st}[0-9][0-9][0-9][0-9][0-9]{dec_year}.pl"))
    prog = 0
    incr = 100 // (2 + len(seg_files))
    segs: list[pd.DataFrame] = []
    for s in seg_files:
        seg_no = s.stem[2:-4]
        segs.append(
            pd.read_csv(
                s,
                delimiter=',' if dec_year == '2010' else '|',
                header=None,
                names=header_dict[dec_year][seg_no].keys(),
                dtype=header_dict[dec_year][seg_no],
                index_col="LOGRECNO"
            )
        )
        prog += incr
        progress(prog)

    geo_path = path / f'{st}geo{dec_year}.pl'
    if dec_year == "2020":
        try:
            geo = pd.read_csv(
                geo_path,
                delimiter='|',
                header=None,
                names=header_dict[dec_year]['Geoheader'].keys(),
                dtype=header_dict[dec_year]['Geoheader'],
                index_col="LOGRECNO"
            )
        except UnicodeDecodeError:
            # the exception is used to deal with particular characters that may appear in
            # some City, VTD, County, or other names, such as ~
            geo = pd.read_csv(
                geo_path,
                delimiter='|',
                header=None,
                names=header_dict[dec_year]['Geoheader'].keys(),
                dtype=header_dict[dec_year]['Geoheader'],
                encoding='latin-1',
                index_col="LOGRECNO"
            )
    else:
        geo = pd.read_fwf(
            geo_path,
            widths=field_widths_2010,
            names=header_dict[dec_year]['Geoheader'].keys(),
            dtype=header_dict[dec_year]['Geoheader'],
            index_col="LOGRECNO"
        )
    prog += incr
    progress(prog)

    geo = geo.drop(columns=['CIFSN'])
    drop_cols = ['FILEID', 'STUSAB', 'CHARITER', 'CIFSN']
    segs = [df.drop(columns=drop_cols) for df in segs]

    pl = geo.join(segs)
    del segs
    pl = pl.rename(str.lower, axis=1)

    # Create GEOID field for the merge to the shapefiles later
    if dec_year == "2010":
        pl = pl.copy()  # without this, the next line gives a fragmented dataframe warning

        # for 2010, have to construct the geoid from its component parts
        pl['geoid'] = None
        for l, fields in geoids.items():
            if not pl[pl['sumlev'] == l].empty:
                pl.loc[pl['sumlev'] == l, 'geoid'] = \
                    pl.loc[pl['sumlev'] == l, fields[0]].str.cat(pl.loc[pl['sumlev'] == l, fields[1:]])
    else:
        # for 2020, strip off everything before the state fips
        pl['geoid'] = pl['geoid'].str[9:]

    progress(100)
    return pl


def join_pl_to_shape(shp_df: gpd.GeoDataFrame, dec_year, geog, pl_data: pd.DataFrame) -> gpd.GeoDataFrame:
    def add_field(fld: str):
        fld = fld.format(dec_yy=dec_year[-2:])
        if fld in shp_df.columns and fld not in sumlev_pl.columns:
            shape_fields.add(fld)

    if isinstance(geographies[geog].level, list):
        sumlev_pl = pl_data[pl_data["sumlev"].isin(geographies[geog].level)]
    else:
        sumlev_pl = pl_data[pl_data["sumlev"] == geographies[geog].level]

    shape_fields = {"geometry"}

    # use name in shapefile
    if f"name{dec_year[-2:]}" in shp_df.columns:
        sumlev_pl = sumlev_pl.drop(columns="name")
        shp_df = shp_df.rename(columns={f"name{dec_year[-2:]}": "name"},)
        shape_fields.add("name")

    for f in geographies[geog].fields:
        if f["source"]:
            for f1 in f["source"]:
                add_field(f1)

    return shp_df[list(shape_fields)].join(sumlev_pl.set_index("geoid", drop=False), how="left")


def load_shape(st, dec_year, geog, src_path: pathlib.Path) -> gpd.GeoDataFrame:
    shp = f"tl_{dec_year}_{states[st].fips}_{geographies[geog].shp}{dec_year[2:]}.zip"
    shp_path = src_path / shp
    if not shp_path.exists():
        return None

    shp_df: gpd.GeoDataFrame = gpd.read_file(shp_path)

    if geog == "aiannh":
        # apparently, the geoid for AIANNHAs in the TIGER/LINE ShapeFile
        # excludes the state fips so we have to prepend it to the geoid

        shp_df[f"GEOID{dec_year[-2:]}"] = shp_df[f"STATEFP{dec_year[-2:]}"] + \
            shp_df[f"GEOID{dec_year[-2:]}"]

    return shp_df.rename(columns=str.lower).set_index(f"geoid{dec_year[-2:]}")


def make_shape(
    geog,
    block_shp: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """create a shapefile by aggregating blocks up to the relevant geography"""
    if isinstance(geographies[geog].level, list):
        source_fields = []
        for l in geographies[geog].level:
            source_fields.extend(f for f in geoids[l] if f not in source_fields)
    else:
        source_fields = geoids[geographies[geog].level]

    fields = []
    for f in source_fields:
        for fld in geographies['b'].fields:
            if (len(fld['source']) == 1 and fld['source'][0] == f):
                fields.append(fld['field'])
            elif (len(fld['source']) == 0 and fld['field'] == f):
                fields.append(fld['field'])

    shp_df: gpd.GeoDataFrame = block_shp[fields + ["geometry"]]
    shp_df = shp_df[~shp_df.isnull().any(axis=1)]
    if shp_df.empty:
        return None

    shp_df = shp_df.dissolve(fields, as_index=False)
    shp_df["geoid"] = shp_df[fields].agg("".join, axis=1)

    return shp_df.drop(columns=fields).set_index("geoid")


def create_block_df(st: str, dec_year: str, pl_data: pd.DataFrame, src_path: pathlib.Path):
    """Create a GeoDataFrame for census blocks without the population fields
        for use in creating geographies for units that don't have a TigerLine shapefile

    Arguments:
        st {str} -- State code
        dec_year {str} -- Decennial census year
        pl_data {pd.DataFrame} -- tabulated pl data
        src_path {pathlib.Path} -- path to shapefiles

    Returns:
        gpd.GeoDataFrame|None -- the census block dataframe
    """
    df = load_shape(st, dec_year, 'b', src_path)
    if df is None:
        return None

    df = join_pl_to_shape(df, dec_year, 'b', pl_data)
    df = add_geog_fields(df, 'b', dec_year)
    return df


def add_geog_fields(gdf: gpd.GeoDataFrame, geog: str, dec_year):
    rename_fields = {
        f["source"][0].format(dec_yy=dec_year[2:]): f["field"]
        for f in geographies[geog].fields
        if len(f["source"]) == 1
    }
    agg_fields = [f for f in geographies[geog].fields if len(f["source"]) > 1]

    agg_cols: dict[str, pd.Series] = {}
    for f in agg_fields:
        flds = [fld.format(dec_yy=dec_year[2:]) for fld in f["source"]]
        agg_cols[f["field"]] = gdf[flds[0]].str.cat(gdf[flds[1:]])

    gdf = gdf.rename(columns=rename_fields)
    gdf = pd.concat([gdf, pd.DataFrame.from_dict(agg_cols)], axis=1)

    for f in geographies[geog].fields:
        if "null" in f:
            gdf.loc[gdf[f["field"]].str.endswith(f["null"]), f["field"]] = None

    gdf = gdf.replace({pd.NA: None})

    return gdf


def add_pop_fields(gdf: gpd.GeoDataFrame):
    dec_pop_fields = [f for f in pop_fields if set(
        f["source"]) & set(gdf.columns)]

    rename_fields = {
        f["source"][0]: f["field"]
        for f in dec_pop_fields
        if len(f["source"]) == 1
    }
    agg_fields = [f for f in dec_pop_fields if len(f["source"]) > 1]
    pct_fields = [f for f in dec_pop_fields if f["total"]]

    # add computed cols
    add_cols: dict[str, pd.Series] = {}
    for f in agg_fields:
        add_cols[f["field"]] = gdf[f["source"]].sum(axis=1)

    gdf = pd.concat([gdf, pd.DataFrame.from_dict(add_cols)], axis=1)

    # rename pl cols
    gdf = gdf.rename(columns=rename_fields)

    # add pct cols
    add_cols = {}
    for f in pct_fields:
        add_cols[f"pct_{f['field']}"] = gdf[f["field"]].div(gdf[f["total"]]).replace(np.inf, None)
    gdf = pd.concat([gdf, pd.DataFrame.from_dict(add_cols)], axis=1)

    gdf = gdf.drop(columns=gdf.columns[gdf.columns.str.startswith(('p00', 'h00'))])

    return gdf


def table_name(geog: str, dec_year: str):
    return f'{geographies[geog].name}{dec_year[-2:]}'


def create_table_script(geog, dec_year):
    table = table_name(geog, dec_year)

    fields = geographies[geog].fields
    create_table_fields = ",\n" \
        .join(f'{f["field"]} {f["type"]} {f["constraint"]}'.strip() for f in fields) \
        .format(dec_yyyy=dec_year, dec_yy=dec_year[-2:], geog=geog)

    create_pop_fields = ",\n".join(
        f'{p["field"]} {p["type"]}' for p in pop_fields
    )
    create_pct_fields = ',\n'.join(
        f'pct_{f["field"]} REAL' for f in pop_fields if f["total"]
    )
    create_table_fields = ",\n".join(
        [create_table_fields, create_pop_fields, create_pct_fields])

    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table} 
            (fid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            {create_table_fields});
        """

    create_indices = geographies[geog].indices.format(
        dec_yyyy=dec_year, dec_yy=dec_year[2:])

    return f"{create_table_sql}\n{create_indices}"


def insert_data_script(geog, dec_year, fields):
    insert_table_fields = f"{','.join(fields[:-1])},geom".format(dec_yy=dec_year[2:])
    params = f"{','.join(f':{f}' for f in fields[:-1])},ST_GeomFromText(:geometry)"
    return f"INSERT INTO {table_name(geog, dec_year)} ({insert_table_fields}) VALUES ({params})"


def create_layer(db: sqlite3.Connection, df: gpd.GeoDataFrame, dec_year: str, geog: str):
    logging.info("Creating layer for %s %s...", dec_year, geographies[geog].descrip)
    success, _ = createGpkgTable(
        db, table_name(geog, dec_year), create_table_script(geog, dec_year), srid=df.crs.to_epsg()
    )
    if not success:
        return False

    fields = [fld["field"] for fld in geographies[geog].fields if fld["field"] in df.columns]
    fields.extend(fld["field"] for fld in pop_fields if fld["field"] in df.columns)
    fields.extend(f"pct_{fld['field']}" for fld in pop_fields if fld["total"] and fld["field"] in df.columns)
    fields.append("geometry")

    sql = insert_data_script(geog, dec_year, fields)
    df['geometry'] = df['geometry'].apply(wkt.dumps)
    db.executemany(sql, df[fields].itertuples(index=False))

    return True


def create_df_for_geog(
    st: str,
    dec_year: str,
    geog: str,
    pl_df: pd.DataFrame,
    shp_path: pathlib.Path = None,
    shp: gpd.GeoDataFrame = None
) -> gpd.GeoDataFrame:
    if shp is None and shp_path is None:
        raise TypeError("Either shp or shp_path must be provided")

    if shp is None:
        df = load_shape(st, dec_year, geog, shp_path)
        if df is None:
            return None
    else:
        df = shp

    df = join_pl_to_shape(df, dec_year, geog, pl_df)
    df = add_geog_fields(df, geog, dec_year)
    df = add_pop_fields(df)
    return df


def create_decennial_layers(
    gpkg: pathlib.Path,
    st: str,
    dec_year: str,
    geogs: Optional[list[str]],
    cache_path: Optional[pathlib.Path] = None,
    progress: Callable[[Union[int, float]], None] = null_progress
):
    if not gpkg.exists():
        raise ValueError("GeoPackage does not exist")

    cache_path = cache_path or pathlib.Path(mkdtemp())

    if geogs is None:
        geogs = list(geographies.keys())

    pl_path = download_and_extract_pl(st, dec_year, cache_path, partial_progress(0, 10, progress))
    shp_path = download_shapefiles(st, dec_year, geogs, cache_path, partial_progress(10, 20, progress))

    pl_df = load_pl_data(st, dec_year, pl_path, partial_progress(20, 40, progress))

    block_df = None

    with spatialite_connect(gpkg) as db:
        c = 60 // len(geogs)
        t = 40
        for g in geogs:
            df = create_df_for_geog(st, dec_year, g, pl_df, shp_path)
            if df is None:
                logging.info("Assembling geography for %s %s...", dec_year, geographies[g].descrip)
                if block_df is None:
                    block_df = create_block_df(st, dec_year, pl_df, shp_path)
                df = make_shape(g, block_df)
                if df is None:
                    continue

                df = create_df_for_geog(st, dec_year, g, pl_df, shp=df)

            if g == "b":
                block_df = df

            create_layer(db, df, dec_year, g)

            t += c
            progress(t)

    progress(100)
    return True
