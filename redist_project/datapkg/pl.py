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
import ftplib
import logging
import pathlib
import re
import sqlite3
import zipfile
from collections.abc import Callable
from tempfile import mkdtemp

import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj
import requests

try:
    import pyogrio
    use_pyogrio = True
except ImportError:
    use_pyogrio = False


from .geography import geographies
from .population import pop_fields
from .state import states
from .utils import spatialite_connect

header_dict: dict[str, dict[str, dict[str, type]]] = {
    "2020": {
        'Geoheader': {"FILEID": "string", "STUSAB": "string", "SUMLEV": "string", "GEOVAR": "string", "GEOCOMP": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "Int64", "GEOID": "string", "GEOCODE": "string", "REGION": "string", "DIVISION": "string", "STATE": "string", "STATENS": "string", "COUNTY": "string", "COUNTYCC": "string", "COUNTYNS": "string", "COUSUB": "string", "COUSUBCC": "string", "COUSUBNS": "string", "SUBMCD": "string", "SUBMCDCC": "string", "SUBMCDNS": "string", "ESTATE": "string", "ESTATECC": "string", "ESTATENS": "string", "CONCIT": "string", "CONCITCC": "string", "CONCITNS": "string", "PLACE": "string", "PLACECC": "string", "PLACENS": "string", "TRACT": "string", "BLKGRP": "string", "BLOCK": "string", "AIANHH": "string", "AIHHTLI": "string", "AIANHHFP": "string", "AIANHHCC": "string", "AIANHHNS": "string", "AITS": "string", "AITSFP": "string", "AITSCC": "string", "AITSNS": "string", "TTRACT": "string", "TBLKGRP": "string", "ANRC": "string", "ANRCCC": "string", "ANRCNS": "string", "CBSA": "string", "MEMI": "string", "CSA": "string", "METDIV": "string", "NECTA": "string", "NMEMI": "string", "CNECTA": "string", "NECTADIV": "string", "CBSAPCI": "string", "NECTAPCI": "string", "UA": "string", "UATYPE": "string", "UR": "string", "CD116": "string", "CD118": "string", "CD119": "string", "CD120": "string", "CD121": "string", "SLDU18": "string", "SLDU22": "string", "SLDU24": "string", "SLDU26": "string", "SLDU28": "string", "SLDL18": "string", "SLDL22": "string", "SLDL24": "string", "SLDL26": "string", "SLDL28": "string", "VTD": "string", "VTDI": "string", "ZCTA": "string", "SDELM": "string", "SDSEC": "string", "SDUNI": "string", "PUMA": "string", "AREALAND": "string", "AREAWATR": "string", "BASENAME": "string", "NAME": "string", "FUNCSTAT": "string", "GCUNI": "string", "POP100": "Int64", "HU100": "Int64", "INTPTLAT": "string", "INTPTLON": "string", "LSADC": "string", "PARTFLAG": "string", "UGA": "string"},
        '00001': {"FILEID": "string", "STUSAB": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "Int64", "P0010001": 'int', "P0010002": 'int', "P0010003": 'int', "P0010004": 'int', "P0010005": 'int', "P0010006": 'int', "P0010007": 'int', "P0010008": 'int', "P0010009": 'int', "P0010010": 'int', "P0010011": 'int', "P0010012": 'int', "P0010013": 'int', "P0010014": 'int', "P0010015": 'int', "P0010016": 'int', "P0010017": 'int', "P0010018": 'int', "P0010019": 'int', "P0010020": 'int', "P0010021": 'int', "P0010022": 'int', "P0010023": 'int', "P0010024": 'int', "P0010025": 'int', "P0010026": 'int', "P0010027": 'int', "P0010028": 'int', "P0010029": 'int', "P0010030": 'int', "P0010031": 'int', "P0010032": 'int', "P0010033": 'int', "P0010034": 'int', "P0010035": 'int', "P0010036": 'int', "P0010037": 'int', "P0010038": 'int', "P0010039": 'int', "P0010040": 'int', "P0010041": 'int', "P0010042": 'int', "P0010043": 'int', "P0010044": 'int', "P0010045": 'int', "P0010046": 'int', "P0010047": 'int', "P0010048": 'int', "P0010049": 'int', "P0010050": 'int', "P0010051": 'int', "P0010052": 'int', "P0010053": 'int', "P0010054": 'int', "P0010055": 'int', "P0010056": 'int', "P0010057": 'int', "P0010058": 'int', "P0010059": 'int', "P0010060": 'int', "P0010061": 'int', "P0010062": 'int', "P0010063": 'int', "P0010064": 'int', "P0010065": 'int', "P0010066": 'int', "P0010067": 'int', "P0010068": 'int', "P0010069": 'int', "P0010070": 'int', "P0010071": 'int', "P0020001": 'int', "P0020002": 'int', "P0020003": 'int', "P0020004": 'int', "P0020005": 'int', "P0020006": 'int', "P0020007": 'int', "P0020008": 'int', "P0020009": 'int', "P0020010": 'int', "P0020011": 'int', "P0020012": 'int', "P0020013": 'int', "P0020014": 'int', "P0020015": 'int', "P0020016": 'int', "P0020017": 'int', "P0020018": 'int', "P0020019": 'int', "P0020020": 'int', "P0020021": 'int', "P0020022": 'int', "P0020023": 'int', "P0020024": 'int', "P0020025": 'int', "P0020026": 'int', "P0020027": 'int', "P0020028": 'int', "P0020029": 'int', "P0020030": 'int', "P0020031": 'int', "P0020032": 'int', "P0020033": 'int', "P0020034": 'int', "P0020035": 'int', "P0020036": 'int', "P0020037": 'int', "P0020038": 'int', "P0020039": 'int', "P0020040": 'int', "P0020041": 'int', "P0020042": 'int', "P0020043": 'int', "P0020044": 'int', "P0020045": 'int', "P0020046": 'int', "P0020047": 'int', "P0020048": 'int', "P0020049": 'int', "P0020050": 'int', "P0020051": 'int', "P0020052": 'int', "P0020053": 'int', "P0020054": 'int', "P0020055": 'int', "P0020056": 'int', "P0020057": 'int', "P0020058": 'int', "P0020059": 'int', "P0020060": 'int', "P0020061": 'int', "P0020062": 'int', "P0020063": 'int', "P0020064": 'int', "P0020065": 'int', "P0020066": 'int', "P0020067": 'int', "P0020068": 'int', "P0020069": 'int', "P0020070": 'int', "P0020071": 'int', "P0020072": 'int', "P0020073": 'int'},
        '00002': {"FILEID": "string", "STUSAB": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "Int64", "P0030001": 'int', "P0030002": 'int', "P0030003": 'int', "P0030004": 'int', "P0030005": 'int', "P0030006": 'int', "P0030007": 'int', "P0030008": 'int', "P0030009": 'int', "P0030010": 'int', "P0030011": 'int', "P0030012": 'int', "P0030013": 'int', "P0030014": 'int', "P0030015": 'int', "P0030016": 'int', "P0030017": 'int', "P0030018": 'int', "P0030019": 'int', "P0030020": 'int', "P0030021": 'int', "P0030022": 'int', "P0030023": 'int', "P0030024": 'int', "P0030025": 'int', "P0030026": 'int', "P0030027": 'int', "P0030028": 'int', "P0030029": 'int', "P0030030": 'int', "P0030031": 'int', "P0030032": 'int', "P0030033": 'int', "P0030034": 'int', "P0030035": 'int', "P0030036": 'int', "P0030037": 'int', "P0030038": 'int', "P0030039": 'int', "P0030040": 'int', "P0030041": 'int', "P0030042": 'int', "P0030043": 'int', "P0030044": 'int', "P0030045": 'int', "P0030046": 'int', "P0030047": 'int', "P0030048": 'int', "P0030049": 'int', "P0030050": 'int', "P0030051": 'int', "P0030052": 'int', "P0030053": 'int', "P0030054": 'int', "P0030055": 'int', "P0030056": 'int', "P0030057": 'int', "P0030058": 'int', "P0030059": 'int', "P0030060": 'int', "P0030061": 'int', "P0030062": 'int', "P0030063": 'int', "P0030064": 'int', "P0030065": 'int', "P0030066": 'int', "P0030067": 'int', "P0030068": 'int', "P0030069": 'int', "P0030070": 'int', "P0030071": 'int', "P0040001": 'int', "P0040002": 'int', "P0040003": 'int', "P0040004": 'int', "P0040005": 'int', "P0040006": 'int', "P0040007": 'int', "P0040008": 'int', "P0040009": 'int', "P0040010": 'int', "P0040011": 'int', "P0040012": 'int', "P0040013": 'int', "P0040014": 'int', "P0040015": 'int', "P0040016": 'int', "P0040017": 'int', "P0040018": 'int', "P0040019": 'int', "P0040020": 'int', "P0040021": 'int', "P0040022": 'int', "P0040023": 'int', "P0040024": 'int', "P0040025": 'int', "P0040026": 'int', "P0040027": 'int', "P0040028": 'int', "P0040029": 'int', "P0040030": 'int', "P0040031": 'int', "P0040032": 'int', "P0040033": 'int', "P0040034": 'int', "P0040035": 'int', "P0040036": 'int', "P0040037": 'int', "P0040038": 'int', "P0040039": 'int', "P0040040": 'int', "P0040041": 'int', "P0040042": 'int', "P0040043": 'int', "P0040044": 'int', "P0040045": 'int', "P0040046": 'int', "P0040047": 'int', "P0040048": 'int', "P0040049": 'int', "P0040050": 'int', "P0040051": 'int', "P0040052": 'int', "P0040053": 'int', "P0040054": 'int', "P0040055": 'int', "P0040056": 'int', "P0040057": 'int', "P0040058": 'int', "P0040059": 'int', "P0040060": 'int', "P0040061": 'int', "P0040062": 'int', "P0040063": 'int', "P0040064": 'int', "P0040065": 'int', "P0040066": 'int', "P0040067": 'int', "P0040068": 'int', "P0040069": 'int', "P0040070": 'int', "P0040071": 'int', "P0040072": 'int', "P0040073": 'int', "H0010001": 'int', "H0010002": 'int', "H0010003": 'int'},
        '00003': {"FILEID": "string", "STUSAB": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "Int64", "P0050001": 'int', "P0050002": 'int', "P0050003": 'int', "P0050004": 'int', "P0050005": 'int', "P0050006": 'int', "P0050007": 'int', "P0050008": 'int', "P0050009": 'int', "P0050010": 'int'},
    },
    "2010": {
        'Geoheader': {"FILEID": "string", "STUSAB": "string", "SUMLEV": "string", "GEOCOMP": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "Int64", "REGION": "string", "DIVISION": "string", "STATE": "string", "COUNTY": "string", "COUNTYCC": "string", "COUNTYSC": "string", "COUSUB": "string", "COUSUBCC": "string", "COUSUBSC": "string", "PLACE": "string", "PLACECC": "string", "PLACESC": "string", "TRACT": "string", "BLKGRP": "string", "BLOCK": "string", "IUC": "string", "CONCIT": "string", "CONCITCC": "string", "CONCITSC": "string", "AIANHH": "string", "AIANHHFP": "string", "AIANHHCC": "string", "AIHHTLI": "string", "AITSCE": "string", "AITS": "string", "AITSCC": "string", "TTRACT": "string", "TBLKGRP": "string", "ANRC": "string", "ANRCCC": "string", "CBSA": "string", "CBSASC": "string", "METDIV": "string", "CSA": "string", "NECTA": "string", "NECTASC": "string", "NECTADIV": "string", "CNECTA": "string", "CBSAPCI": "string", "NECTAPCI": "string", "UA": "string", "UASC": "string", "UATYPE": "string", "UR": "string", "CD": "string", "SLDU": "string", "SLDL": "string", "VTD": "string", "VTDI": "string", "RESERVE2": "string", "ZCTA5": "string", "SUBMCD": "string", "SUBMCDCC": "string", "SDELM": "string", "SDSEC": "string", "SDUNI": "string", "AREALAND": "string", "AREAWATR": "string", "NAME": "string", "FUNCSTAT": "string", "GCUNI": "string", "POP100": "string", "HU100": "string", "INTPTLAT": "string", "INTPTLON": "string", "LSADC": "string", "PARTFLAG": "string", "RESERVE3": "string", "UGA": "string", "STATENS": "string", "COUNTYNS": "string", "COUSUBNS": "string", "PLACENS": "string", "CONCITNS": "string", "AIANHHNS": "string", "AITSNS": "string", "ANRCNS": "string", "SUBMCDNS": "string", "CD113": "string", "CD114": "string", "CD115": "string", "SLDU2": "string", "SLDU3": "string", "SLDU4": "string", "SLDL2": "string", "SLDL3": "string", "SLDL4": "string", "AIANHHSC": "string", "CSASC": "string", "CNECTASC": "string", "MEMI": "string", "NMEMI": "string", "PUMA": "string", "RESERVED": "string"},
        '00001': {"FILEID": "string", "STUSAB": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "Int64", "P0010001": 'int', "P0010002": 'int', "P0010003": 'int', "P0010004": 'int', "P0010005": 'int', "P0010006": 'int', "P0010007": 'int', "P0010008": 'int', "P0010009": 'int', "P0010010": 'int', "P0010011": 'int', "P0010012": 'int', "P0010013": 'int', "P0010014": 'int', "P0010015": 'int', "P0010016": 'int', "P0010017": 'int', "P0010018": 'int', "P0010019": 'int', "P0010020": 'int', "P0010021": 'int', "P0010022": 'int', "P0010023": 'int', "P0010024": 'int', "P0010025": 'int', "P0010026": 'int', "P0010027": 'int', "P0010028": 'int', "P0010029": 'int', "P0010030": 'int', "P0010031": 'int', "P0010032": 'int', "P0010033": 'int', "P0010034": 'int', "P0010035": 'int', "P0010036": 'int', "P0010037": 'int', "P0010038": 'int', "P0010039": 'int', "P0010040": 'int', "P0010041": 'int', "P0010042": 'int', "P0010043": 'int', "P0010044": 'int', "P0010045": 'int', "P0010046": 'int', "P0010047": 'int', "P0010048": 'int', "P0010049": 'int', "P0010050": 'int', "P0010051": 'int', "P0010052": 'int', "P0010053": 'int', "P0010054": 'int', "P0010055": 'int', "P0010056": 'int', "P0010057": 'int', "P0010058": 'int', "P0010059": 'int', "P0010060": 'int', "P0010061": 'int', "P0010062": 'int', "P0010063": 'int', "P0010064": 'int', "P0010065": 'int', "P0010066": 'int', "P0010067": 'int', "P0010068": 'int', "P0010069": 'int', "P0010070": 'int', "P0010071": 'int', "P0020001": 'int', "P0020002": 'int', "P0020003": 'int', "P0020004": 'int', "P0020005": 'int', "P0020006": 'int', "P0020007": 'int', "P0020008": 'int', "P0020009": 'int', "P0020010": 'int', "P0020011": 'int', "P0020012": 'int', "P0020013": 'int', "P0020014": 'int', "P0020015": 'int', "P0020016": 'int', "P0020017": 'int', "P0020018": 'int', "P0020019": 'int', "P0020020": 'int', "P0020021": 'int', "P0020022": 'int', "P0020023": 'int', "P0020024": 'int', "P0020025": 'int', "P0020026": 'int', "P0020027": 'int', "P0020028": 'int', "P0020029": 'int', "P0020030": 'int', "P0020031": 'int', "P0020032": 'int', "P0020033": 'int', "P0020034": 'int', "P0020035": 'int', "P0020036": 'int', "P0020037": 'int', "P0020038": 'int', "P0020039": 'int', "P0020040": 'int', "P0020041": 'int', "P0020042": 'int', "P0020043": 'int', "P0020044": 'int', "P0020045": 'int', "P0020046": 'int', "P0020047": 'int', "P0020048": 'int', "P0020049": 'int', "P0020050": 'int', "P0020051": 'int', "P0020052": 'int', "P0020053": 'int', "P0020054": 'int', "P0020055": 'int', "P0020056": 'int', "P0020057": 'int', "P0020058": 'int', "P0020059": 'int', "P0020060": 'int', "P0020061": 'int', "P0020062": 'int', "P0020063": 'int', "P0020064": 'int', "P0020065": 'int', "P0020066": 'int', "P0020067": 'int', "P0020068": 'int', "P0020069": 'int', "P0020070": 'int', "P0020071": 'int', "P0020072": 'int', "P0020073": 'int'},
        '00002': {"FILEID": "string", "STUSAB": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "Int64", "P0030001": 'int', "P0030002": 'int', "P0030003": 'int', "P0030004": 'int', "P0030005": 'int', "P0030006": 'int', "P0030007": 'int', "P0030008": 'int', "P0030009": 'int', "P0030010": 'int', "P0030011": 'int', "P0030012": 'int', "P0030013": 'int', "P0030014": 'int', "P0030015": 'int', "P0030016": 'int', "P0030017": 'int', "P0030018": 'int', "P0030019": 'int', "P0030020": 'int', "P0030021": 'int', "P0030022": 'int', "P0030023": 'int', "P0030024": 'int', "P0030025": 'int', "P0030026": 'int', "P0030027": 'int', "P0030028": 'int', "P0030029": 'int', "P0030030": 'int', "P0030031": 'int', "P0030032": 'int', "P0030033": 'int', "P0030034": 'int', "P0030035": 'int', "P0030036": 'int', "P0030037": 'int', "P0030038": 'int', "P0030039": 'int', "P0030040": 'int', "P0030041": 'int', "P0030042": 'int', "P0030043": 'int', "P0030044": 'int', "P0030045": 'int', "P0030046": 'int', "P0030047": 'int', "P0030048": 'int', "P0030049": 'int', "P0030050": 'int', "P0030051": 'int', "P0030052": 'int', "P0030053": 'int', "P0030054": 'int', "P0030055": 'int', "P0030056": 'int', "P0030057": 'int', "P0030058": 'int', "P0030059": 'int', "P0030060": 'int', "P0030061": 'int', "P0030062": 'int', "P0030063": 'int', "P0030064": 'int', "P0030065": 'int', "P0030066": 'int', "P0030067": 'int', "P0030068": 'int', "P0030069": 'int', "P0030070": 'int', "P0030071": 'int', "P0040001": 'int', "P0040002": 'int', "P0040003": 'int', "P0040004": 'int', "P0040005": 'int', "P0040006": 'int', "P0040007": 'int', "P0040008": 'int', "P0040009": 'int', "P0040010": 'int', "P0040011": 'int', "P0040012": 'int', "P0040013": 'int', "P0040014": 'int', "P0040015": 'int', "P0040016": 'int', "P0040017": 'int', "P0040018": 'int', "P0040019": 'int', "P0040020": 'int', "P0040021": 'int', "P0040022": 'int', "P0040023": 'int', "P0040024": 'int', "P0040025": 'int', "P0040026": 'int', "P0040027": 'int', "P0040028": 'int', "P0040029": 'int', "P0040030": 'int', "P0040031": 'int', "P0040032": 'int', "P0040033": 'int', "P0040034": 'int', "P0040035": 'int', "P0040036": 'int', "P0040037": 'int', "P0040038": 'int', "P0040039": 'int', "P0040040": 'int', "P0040041": 'int', "P0040042": 'int', "P0040043": 'int', "P0040044": 'int', "P0040045": 'int', "P0040046": 'int', "P0040047": 'int', "P0040048": 'int', "P0040049": 'int', "P0040050": 'int', "P0040051": 'int', "P0040052": 'int', "P0040053": 'int', "P0040054": 'int', "P0040055": 'int', "P0040056": 'int', "P0040057": 'int', "P0040058": 'int', "P0040059": 'int', "P0040060": 'int', "P0040061": 'int', "P0040062": 'int', "P0040063": 'int', "P0040064": 'int', "P0040065": 'int', "P0040066": 'int', "P0040067": 'int', "P0040068": 'int', "P0040069": 'int', "P0040070": 'int', "P0040071": 'int', "P0040072": 'int', "P0040073": 'int', "H0010001": 'int', "H0010002": 'int', "H0010003": 'int'},
        '00003': {"FILEID": "string", "STUSAB": "string", "CHARITER": "string", "CIFSN": "string", "LOGRECNO": "Int64", "P0050001": 'int', "P0050002": 'int', "P0050003": 'int', "P0050004": 'int', "P0050005": 'int', "P0050006": 'int', "P0050007": 'int', "P0050008": 'int', "P0050009": 'int', "P0050010": 'int'},
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

URLS = {
    "2020": {
        # "field_def": "https://www2.census.gov/programs-surveys/decennial/rdo/about/{year}-census-program/Phase3/SupportMaterials/{year}_PLSummaryFile_FieldNames.xlsx",
        # "baf": "https://www2.census.gov/geo/docs/maps-data/data/baf{year}/BlockAssign_ST{fips}_{st_caps}.zip",
        "pl_data": "https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/{state}/{st}{year}.pl.zip",
        "shape": "https://www2.census.gov/geo/tiger/TIGER2020PL/STATE/{fips}_{state_caps}/{fips}/tl_{year}_{fips}_{{geog}}{yy}.zip"
    },
    "2010": {
        # "field_def": "https://www2.census.gov/census_{year}/01-Redistricting_File--PL_94-171/0FILE_STRUCTURE.doc",
        # "baf": "https://www2.census.gov/geo/docs/maps-data/data/baf/BlockAssign_ST{fips}_{st_caps}.zip",
        "pl_data": "https://www2.census.gov/census_{year}/01-Redistricting_File--PL_94-171/{state}/{st}{year}.pl.zip",
        "shape": "https://www2.census.gov/geo/pvs/tiger{year}st/{fips}_{state}/{fips}/tl_{year}_{fips}_{{geog}}{yy}.zip"
    }
}


def download(
    url: str,
    dest_path: pathlib.Path,
    extract_to: pathlib.Path = None,
    progress: Callable[[int | float], None] = None
):
    r = requests.get(url, allow_redirects=True, timeout=60, stream=True)
    if not r.ok:
        return False

    block_size = 4096
    with dest_path.open('wb+') as file:
        for data in r.iter_content(block_size):
            if progress:
                progress(len(data))
            file.write(data)

    if dest_path.suffix == '.zip' and extract_to:
        with zipfile.ZipFile(dest_path, "r") as z:
            z.extractall(extract_to)

    return True


def download_decennial(st: str, dec_year: str = "2020", dest_path: pathlib.Path = None, progress: Callable[[float], None] = None):
    def prog(b):
        if progress:
            nonlocal count
            if total != 0:
                count += b
                progress(100 * count/total)
            else:
                progress(100 * count/len(urldict))

    def check_file(url):
        path = url.removeprefix("https://www2.census.gov")
        if ftp.nlst(path):
            nonlocal total
            total += ftp.size(path)
            fname = url.rsplit('/', 1)[1]
            urldict[url] = dest_path / fname
        else:
            return None, None

    urldict: dict[str, pathlib.Path] = {}
    total = 0
    count = 0

    # census webserver doesn't return size info on HEAD command, so use FTP
    with ftplib.FTP("ftp2.census.gov", user="Anonymous", passwd="") as ftp:
        for f, urlt in URLS[dec_year].items():
            url = urlt.format(
                st=st,
                year=dec_year,
                yy=dec_year[2:],
                state=states[st].name.replace(' ', '_'),
                state_caps=states[st].name.upper().replace(' ', '_'),
                st_caps=st.upper(),
                fips=states[st].fips
            )

            if f == "shape":
                for _, geog in geographies.items():
                    check_file(url.format(geog=geog.shp))
            else:
                check_file(url)

    for url, file_path in urldict.items():
        if file_path.exists():
            count += file_path.stat().st_size
            prog(0)
            continue

        logging.info("Downloading %s", file_path.name)
        if file_path.suffixes[0] == ".pl":
            extract_to = dest_path / "pl_data"
        else:
            extract_to = dest_path / "shape"
        if not download(url, file_path, extract_to, prog):
            logging.error("Failed to download %s", file_path.name)
            return None

    return dest_path


def load_pl_data(st: str, dec_year, path: pathlib.Path) -> pd.DataFrame:
    path = path / "pl_data"
    segs: list[pd.DataFrame] = []
    for s in path.glob(f"{st}[0-9][0-9][0-9][0-9][0-9]{dec_year}.pl"):
        seg_no = re.search(fr'{st}(\d{{5}}){dec_year}', str(s))[1]
        segs.append(
            pd.read_csv(
                s,
                delimiter='|' if dec_year == '2020' else ',',
                header=None,
                names=header_dict[dec_year][seg_no].keys(),
                dtype=header_dict[dec_year][seg_no],
                index_col="LOGRECNO"
            )
        )

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

    drop_cols = ['FILEID', 'STUSAB', 'CHARITER', 'CIFSN']
    geo.drop(columns=['CIFSN'], inplace=True)
    for df in segs:
        df.drop(columns=drop_cols, inplace=True)

    full_pl = geo.join(segs)
    full_pl.columns = full_pl.columns.str.lower()

    # Create GEOID field for the merge to the shapefiles later
    if dec_year == "2020":
        full_pl['geoid'] = full_pl['geoid'].str[9:]
    else:
        full_pl['geoid'] = None
        for l, fields in geoids.items():
            if not full_pl[full_pl['sumlev'] == l].empty:
                full_pl.loc[full_pl['sumlev'] == l, 'geoid'] = \
                    full_pl.loc[full_pl['sumlev'] == l, fields].sum(axis=1)

    return full_pl


def join_shape(shp_df: gpd.GeoDataFrame, dec_year, geog, pl_data: pd.DataFrame):
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
        shp_df.rename(columns={f"name{dec_year[-2:]}": "name"}, inplace=True)
        shape_fields.add("name")

    for f in geographies[geog].fields:
        if f["source"]:
            for f1 in f["source"]:
                add_field(f1)

    shp_df = shp_df[list(shape_fields)].join(
        sumlev_pl.set_index("geoid", drop=False), how="left")
    return shp_df.copy()


def add_shape(st, dec_year, geog, src_path: pathlib.Path, pl_data: pd.DataFrame) -> gpd.GeoDataFrame:
    shp = f"tl_{dec_year}_{states[st].fips}_{geographies[geog].shp}{dec_year[2:]}.shp"
    shp_path = src_path / "shape" / shp
    if not shp_path.exists():
        return None

    shp_df: gpd.GeoDataFrame
    if use_pyogrio:
        shp_df = pyogrio.read_dataframe(shp_path)
    else:
        shp_df = gpd.read_file(shp_path)

    if geog == "aiannh":
        # apparently, the geoid for AIANNHAs in the TIGER/LINE ShapeFile
        # excludes the state fips so we have to prepend it to the geoid

        shp_df[f"GEOID{dec_year[-2:]}"] = shp_df[f"STATEFP{dec_year[-2:]}"] + \
            shp_df[f"GEOID{dec_year[-2:]}"]
    shp_df.set_index(shp_df[f"GEOID{dec_year[-2:]}"], inplace=True)
    shp_df.rename(columns=str.lower, inplace=True)

    return join_shape(shp_df, dec_year, geog, pl_data)


def make_shape(
    st,
    dec_year,
    geog,
    src_path: pathlib.Path,
    block_shp: gpd.GeoDataFrame,
    pl_data: pd.DataFrame
) -> gpd.GeoDataFrame:
    """create a shapefile by aggregating blocks up to the relevant geography"""
    if isinstance(geographies[geog].level, list):
        source_fields = []
        for l in geographies[geog].level:
            source_fields.append(f for f in l if f not in source_fields)
    else:
        source_fields = geoids[geographies[geog].level]

    fields = []
    for f in source_fields:
        fld = next((x for x in geographies['b'].fields if (len(
            x["source"]) == 1 and x["source"][0] == f) or (len(x["source"]) == 0 and x["field"] == f)), None)
        if fld:
            fields.append(fld["field"])

    if block_shp is None:
        shp_name = f"tl_{dec_year}_{states[st].fips}_{geographies['b'].shp}{dec_year[-2:]}.shp"
        shp_path = src_path / "shape" / shp_name
        if not shp_path.exists():
            return None

        if use_pyogrio:
            block_shp = pyogrio.read_dataframe(
                shp_path, columns=[f"GEOID{dec_year[-2:]}"])
        else:
            block_shp = gpd.read_file(
                shp_path, columns=[f"GEOID{dec_year[-2:]}"])

        block_shp.set_index("GEOID20", inplace=True)
        block_shp = block_shp.join(pl_data.set_index(
            "geoid").loc[pl_data["sumlev"] == 750, fields])
        block_shp.replace(r'^9+$', pd.NA, inplace=True, regex=True)

    shp_df: gpd.GeoDataFrame = block_shp[fields + ["geometry"]
                                         ][~block_shp.isnull().any(axis=1)].dissolve(fields, as_index=False)
    if shp_df.empty:
        return None

    shp_df["geoid"] = shp_df[fields].agg("".join, axis=1)
    shp_df.drop(columns=fields, inplace=True)
    shp_df.set_index("geoid", inplace=True)

    return join_shape(shp_df, dec_year, geog, pl_data)


def add_geog_fields(gdf: gpd.GeoDataFrame, geog: str, dec_year):
    rename_fields = {f["source"][0].format(
        dec_yy=dec_year[2:]): f["field"] for f in geographies[geog].fields if len(f["source"]) == 1}
    agg_fields = [f for f in geographies[geog].fields if len(f["source"]) > 1]

    agg_cols = {}
    for f in agg_fields:
        flds = [fld.format(dec_yy=dec_year[2:]) for fld in f["source"]]
        agg_cols[f["field"]] = gdf[flds].sum(axis=1)

    gdf.rename(columns=rename_fields, inplace=True)
    gdf = pd.concat([gdf, pd.DataFrame.from_dict(agg_cols)],
                    axis=1, copy=False)

    for f in geographies[geog].fields:
        if "null" in f:
            gdf.loc[gdf[f["field"]].str.endswith(f["null"]), f["field"]] = None

    gdf.replace({pd.NA: None}, inplace=True)

    return gdf.copy()


def add_pop_fields(gdf: gpd.GeoDataFrame):
    dec_pop_fields = [f for f in pop_fields if set(
        f["source"]) & set(gdf.columns)]

    rename_fields = {f["source"][0]: f["field"]
                     for f in dec_pop_fields if len(f["source"]) == 1}
    agg_fields = [f for f in dec_pop_fields if len(f["source"]) > 1]
    pct_fields = [f for f in dec_pop_fields if f["total"]]

    # add computed cols
    add_cols = {}
    for f in agg_fields:
        add_cols[f["field"]] = gdf[f["source"]].sum(axis=1)
    gdf = pd.concat([gdf, pd.DataFrame.from_dict(add_cols)],
                    axis=1, copy=False)

    # rename pl cols
    gdf.rename(columns=rename_fields, inplace=True)

    # add pct cols
    add_cols = {}
    for f in pct_fields:
        add_cols[f"pct_{f['field']}"] = gdf[f["field"]].div(
            gdf[f["total"]]).replace(np.inf, None)
    gdf = pd.concat([gdf, pd.DataFrame.from_dict(add_cols)],
                    axis=1, copy=False)

    drop_cols = gdf.columns[gdf.columns.str.startswith(('p00', 'h00'))]
    gdf.drop(columns=drop_cols, inplace=True)

    return gdf.copy()


def create_table_script(geog, year, srid, include_pop_fields=True):
    table = f"{geographies[geog].name}{year[2:]}"

    fields = geographies[geog].fields
    create_table_fields = ",\n" \
        .join(f'{f["field"]} {f["type"]} {f["constraint"]}'.strip() for f in fields) \
        .format(dec_yyyy=year, dec_yy=year[-2:], geog=geog)
    if include_pop_fields:
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

    make_spatial_sql = f"""
        SELECT gpkgAddGeometryColumn("{table}", "geom", "MULTIPOLYGON", 0, 0, {srid});
        SELECT gpkgAddGeometryTriggers("{table}", "geom");
        SELECT gpkgAddSpatialIndex("{table}", "geom");
        INSERT INTO gpkg_ogr_contents (table_name) VALUES ('{table}');
    """

    create_indices = geographies[geog].indices.format(
        dec_yyyy=year, dec_yy=year[2:])

    return f"{create_table_sql}\n{make_spatial_sql}\n{create_indices}"


def insert_data_script(geog, year, fields):
    table = f"{geographies[geog].name}{year[2:]}"
    insert_table_fields = f"{','.join(fields[:-1])},geom".format(
        dec_yy=year[2:])
    params = f"{','.join(f':{f}' for f in fields[:-1])},ST_GeomFromText(:geometry)"
    return f"INSERT INTO {table} ({insert_table_fields}) VALUES ({params})"


def create_layer(db: sqlite3.Connection, df: gpd.GeoDataFrame, dec_year: str, geog: str):
    crs: pyproj.CRS = df.crs
    org, srid = crs.to_authority()
    if org == "EPSG":
        s = db.execute(
            f"SELECT COUNT(srs_id) FROM gpkg_spatial_ref_sys where srs_id = {srid}")
        if s.fetchone()[0] == 0:
            db.execute(f"SELECT gpkgInsertEpsgSRID({srid}")

    s = create_table_script(geog, dec_year, srid)
    db.executescript(s)

    fields = [fld["field"]
              for fld in geographies[geog].fields if fld["field"] in df.columns]
    fields.extend(fld["field"]
                  for fld in pop_fields if fld["field"] in df.columns)
    fields.extend(
        f"pct_{fld['field']}" for fld in pop_fields if fld["total"] and fld["field"] in df.columns)
    fields.append("geometry")

    sql = insert_data_script(geog, dec_year, fields)
    db.executemany(sql, df[fields].to_wkt().itertuples(index=False))
    # df.to_file(gpkg, layer=f"{geographies[g].name}{dec_year[2:]}", driver="GPKG")
    db.execute(
        f"UPDATE gpkg_ogr_contents SET feature_count = (SELECT COUNT(*) FROM {geographies[geog].name}{dec_year[-2:]})"
    )


def process_pl(
    st,
    dec_year,
    gpkg,
    geogs=None,
    src_path: pathlib.Path = None,
    delete_if_exists=True,
    progress: Callable[[float], None] = None
):
    if src_path is None:
        src_path = pathlib.Path(mkdtemp())

    logging.info("Downloading %s PL 94-171 data and shapefiles", dec_year)
    if progress:
        def dl_prog(p): return progress(0.5 * p)
    else:
        dl_prog = None

    src_path = download_decennial(st, dec_year, src_path, progress=dl_prog)

    if geogs is None:
        geogs = list(geographies.keys())

    init_gpkg = True
    if gpkg.exists():
        if delete_if_exists:
            gpkg.unlink()
        else:
            init_gpkg = False

    with spatialite_connect(gpkg) as db:
        if init_gpkg:
            db.execute("SELECT gpkgCreateBaseTables()")
            db.execute(
                "CREATE TABLE gpkg_ogr_contents (table_name TEXT NOT NULL PRIMARY KEY, feature_count INTEGER DEFAULT NULL")

        logging.info("Tabulating %s PL 94-171 data", dec_year)
        pl_data = load_pl_data(st, dec_year, src_path)
        if progress:
            progress(60)
        block_df = None
        for i, g in enumerate(geogs):
            logging.info("Creating layer for %s %s...", dec_year, geographies[g].descrip)
            df = add_shape(st, dec_year, g, src_path, pl_data)
            if df is None:
                df = make_shape(st, dec_year, g, src_path, block_df, pl_data)

            if df is None:
                logging.info("Could not find shapefile for %s %s", dec_year, geographies[g].descrip)
                continue

            df = add_geog_fields(df, g, dec_year)
            df = add_pop_fields(df)

            if g == "b":
                block_df = df

            # pyogrio.write_dataframe(df, gpkg, f"{geographies[g].name}{dec_year[-2:]}", append=True)

            create_layer(db, df, dec_year, g)
            logging.info("\033[Acomplete")
            if progress:
                progress(60 + 40 * i / len(geogs))

    return gpkg
