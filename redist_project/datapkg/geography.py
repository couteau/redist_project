"""QGIS Redistricting Project Plugin - census geography specs

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
from dataclasses import dataclass
from typing import Any


@dataclass
class Geography:
    geog: str
    name: str
    descrip: str
    shp: str
    cvap: str
    level: str
    geoid_len: int
    states: list[str]
    indices: str
    fields: list[dict[str, Any]]


geographies = {
    "b": Geography(
        geog="b",
        name="block",
        descrip="Census Block",
        shp="tabblock",
        cvap=None,
        level="750",
        geoid_len=15,
        states=[],
        indices="""
            CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_vtd ON block{dec_yy} (statefp, countyfp, vtd);
            CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_countyid ON block{dec_yy} (countyid);
            CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_vtdid ON block{dec_yy} (vtdid);
            CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_tractid ON block{dec_yy} (tractid);
            CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_placeid ON block{dec_yy} (placeid);
            CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_cousubid ON block{dec_yy} (cousubid);
            CREATE INDEX IF NOT EXISTS idx_tract{dec_yy}_cbsa ON block{dec_yy} (cbsafp);
            CREATE INDEX IF NOT EXISTS idx_tract{dec_yy}_aiannh ON block{dec_yy} (aianhhce);
        """,
        fields=[
            {"field": "geoid",
                "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": []},
            {"field": "statefp", "type": "TEXT(5)", "constraint": "NOT NULL",
                "source": ["state"]},
            {"field": "countyfp", "type": "TEXT(5)", "constraint": "NOT NULL",
                "source": ["county"]},
            {"field": "countycc",
                "type": "TEXT(5)", "constraint": "", "source": []},
            {"field": "tractce", "type": "TEXT(10)", "constraint": "NOT NULL",
                "source": ["tract"]},
            {"field": "blockce", "type": "TEXT(10)", "constraint": "NOT NULL",
                "source": ["block"]},
            {"field": "blkgrpce", "type": "TEXT(5)", "constraint": "NOT NULL",
                "source": ["blkgrp"]},
            {"field": "aianhhce", "type": "TEXT(4)", "constraint": "",
                "source": ["aianhh"], "null": "9999"},
            {"field": "aianhhcc",
                "type": "TEXT(2)", "constraint": "", "source": []},
            {"field": "aihhtli", "type": "TEXT(1)", "constraint": "",
                "source": [], "null": "9"},
            {"field": "aits", "type": "TEXT(3)", "constraint": "",
                "source": [], "null": "999"},
            {"field": "aitscc",
                "type": "TEXT(2)", "constraint": "", "source": []},
            {"field": "vtd", "type": "TEXT(10)", "constraint": "",
                "source": []},
            {"field": "vtdi", "type": "TEXT(2)", "constraint": "",
                "source": []},
            {"field": "cousub", "type": "TEXT(10)", "constraint": "",
                "source": [], "null": "99999"},
            {"field": "cousubcc",
                "type": "TEXT(2)", "constraint": "", "source": []},
            {"field": "submcd", "type": "TEXT(10)", "constraint": "",
                "source": [], "null": "99999"},
            {"field": "submcdcc",
                "type": "TEXT(2)", "constraint": "", "source": []},
            {"field": "place", "type": "TEXT(10)", "constraint": "",
                "source": [], "null": "99999"},
            {"field": "placecc",
                "type": "TEXT(2)", "constraint": "", "source": []},
            {"field": "concit", "type": "TEXT(5)", "constraint": "",
                "source": [], "null": "99999"},
            {"field": "concitcc",
                "type": "TEXT(2)", "constraint": "", "source": []},
            {"field": "countyid", "type": "TEXT(15)", "constraint": "NOT NULL REFERENCES county{dec_yy} (geoid)",
             "source": ["state", "county"]},
            {"field": "tractid", "type": "TEXT(15)", "constraint": "NOT NULL REFERENCES tract{dec_yy} (geoid)",
             "source": ["state", "county", "tract"]},
            {"field": "blkgrpid", "type": "TEXT(15)", "constraint": "NOT NULL REFERENCES blockgroup{dec_yy} (geoid)",
             "source": ["state", "county", "tract", "blkgrp"]},
            {"field": "vtdid", "type": "TEXT(15)", "constraint": "REFERENCES vtd{dec_yy} (geoid)",
                "source": ["state", "county", "vtd"]},
            {"field": "placeid", "type": "TEXT(15)", "constraint": "REFERENCES place{dec_yy} (geoid)",
             "source": ["state", "place"], "null": "99999"},
            {"field": "cousubid", "type": "TEXT(15)", "constraint": "",
             "source": ["state", "county", "cousub"], "null": "99999"},
            {"field": "cbsafp", "type": "TEXT(5)", "constraint": "",
             "source": ["cbsa"], "null": "99999"},
            {"field": "aiannhid", "type": "TEXT(4)", "constraint": "REFERENCES aiannh{dec_yy} (geoid)",
             "source": ["state", "aianhh", "aihhtli"], "null": "99999"},
            {"field": "concityid", "type": "TEXT(4)", "constraint": "REFERENCES concity{dec_yy} (geoid)",
             "source": ["state", "concit"], "null": "99999"},
        ]
    ),
    "bg": Geography(
        geog="bg", name="blkgrp", descrip="Block Group", shp="bg", cvap="BlockGr", level="150", geoid_len=12,
        states=[],
        indices="""
            CREATE INDEX IF NOT EXISTS idx_blkgrp{dec_yy}_blkgrp ON blkgrp{dec_yy} (statefp,countyfp,tractce,blkgrpce);
            CREATE INDEX IF NOT EXISTS idx_blkgrp{dec_yy}_countyid ON blkgrp{dec_yy} (countyid);
            CREATE INDEX IF NOT EXISTS idx_blkgrp{dec_yy}_tractid ON blkgrp{dec_yy} (tractid);
        """,
        fields=[
            {"field": "geoid",
                "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": []},
            {"field": "statefp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "state"]},
            {"field": "countyfp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "county"]},
            {"field": "tractce", "type": "TEXT(10)", "constraint": "NOT NULL", "source": [
                "tract"]},
            {"field": "blkgrpce", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "blkgrp"]},
            {"field": "countyid", "type": "TEXT(15)",
                "constraint": "NOT NULL REFERENCES county{dec_yy} (geoid)", "source": ["state", "county"]},
            {"field": "tractid", "type": "TEXT(15)",
                "constraint": "NOT NULL REFERENCES tract{dec_yy} (geoid)", "source": ["state", "county", "tract"]},
        ]
    ),
    "city": Geography(
        geog="city", name="concity", descrip="City", shp="concity", cvap=None, level="170", geoid_len=7,
        states=["ct", "ga", "in", "ks", "ky", "mt", "tn"],
        indices="""
            CREATE INDEX IF NOT EXISTS idx_concit{dec_yy}_name ON cousub{dec_yy} (name);
        """,
        fields=[
            {"field": "geoid",
                "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": []},
            {"field": "name", "type": "TEXT",
                "constraint": "NOT NULL", "source": []},
            {"field": "statefp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "state"]},
            {"field": "concitcc",
                "type": "TEXT(2)", "constraint": "", "source": []},
        ]
    ),
    "aiannh": Geography(
        geog="aiannh", name="aiannh",
        descrip="American Indian, Alaska Native, and Native Hawaian Areas",
        shp="aiannh", cvap=None, level=["283", "286"], geoid_len=6,
        states=[],
        indices="""
            CREATE INDEX IF NOT EXISTS idx_aiannh{dec_yy}_aiannh ON aiannh{dec_yy} (aiannhce, comptyp);
        """,
        fields=[
            {"field": "geoid",
                "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": []},
            {"field": "name", "type": "TEXT",
                "constraint": "NOT NULL", "source": []},
            {"field": "statefp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "state"]},
            {"field": "aiannhce", "type": "TEXT(4)", "constraint": "NOT NULL", "source": [
                "aiannhce{dec_yy}"]},
            {"field": "comptyp", "type": "TEXT(5)", "constraint": "", "source": [
                "comptyp{dec_yy}"]},
            {"field": "aiannhr", "type": "TEXT(5)", "constraint": "", "source": [
                "aiannhr{dec_yy}"]},
            {"field": "classfp", "type": "TEXT(5)", "constraint": "", "source": [
                "classfp{dec_yy}"]},
        ]
    ),
    "p": Geography(
        geog="p", name="place", descrip="Census Place", shp="place", cvap="Place", level="160", geoid_len=7,
        states=[],
        indices="""
            CREATE INDEX IF NOT EXISTS idx_place{dec_yy}_place ON place{dec_yy} (statefp, placefp);
        """,
        fields=[
            {"field": "geoid",
                "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": []},
            {"field": "name", "type": "TEXT",
                "constraint": "NOT NULL", "source": []},
            {"field": "statefp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "state"]},
            {"field": "placefp", "type": "TEXT(10)", "constraint": "NOT NULL", "source": [
                "place"]},
            {"field": "classfp", "type": "TEXT(5)", "constraint": "", "source": [
                "classfp{dec_yy}"]},
        ]
    ),
    "cousub": Geography(
        geog="cousub", name="cousub", descrip="County Subdivision", shp="cousub", cvap=None, level="060", geoid_len=10,
        states=[],
        indices="""
            CREATE INDEX IF NOT EXISTS idx_cousub{dec_yy}_vtd ON cousub{dec_yy} (statefp, countyfp, cousub);
            CREATE INDEX IF NOT EXISTS idx_cousub{dec_yy}_county_id ON cousub{dec_yy} (countyid);
            CREATE INDEX IF NOT EXISTS idx_cousub{dec_yy}_name ON cousub{dec_yy} (name);
        """,
        fields=[
            {"field": "geoid",
                "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": []},
            {"field": "name", "type": "TEXT",
                "constraint": "NOT NULL", "source": []},
            {"field": "statefp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "state"]},
            {"field": "countyfp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "county"]},
            {"field": "cousub",
                "type": "TEXT(10)", "constraint": "", "source": []},
            {"field": "cousubcc",
                "type": "TEXT(2)", "constraint": "", "source": []},
            {"field": "countyid", "type": "TEXT(15)",
                "constraint": "NOT NULL REFERENCES county{dec_yy} (geoid)", "source": ["state", "county"]},
        ]
    ),
    "t": Geography(
        geog="t", name="tract", descrip="Tract", shp="tract", cvap="Tract", level="140", geoid_len=11,
        states=[],
        indices="""
            CREATE INDEX IF NOT EXISTS idx_tract{dec_yy}_tract ON tract{dec_yy} (statefp, countyfp, tractce);
            CREATE INDEX IF NOT EXISTS idx_tract{dec_yy}_county_id ON tract{dec_yy} (countyid);
            CREATE INDEX IF NOT EXISTS idx_tract{dec_yy}_cbsa ON tract{dec_yy} (cbsafp);
        """,
        fields=[
            {"field": "geoid",
                "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": []},
            {"field": "statefp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "state"]},
            {"field": "countyfp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "county"]},
            {"field": "tractce", "type": "TEXT(10)", "constraint": "NOT NULL", "source": [
                "tract"]},
            {"field": "cbsafp", "type": "TEXT(5)", "constraint": "", "source": [
                "cbsa"], "null": "99999"},
            {"field": "countyid", "type": "TEXT(15)",
                "constraint": "NOT NULL REFERENCES county{dec_yy} (geoid)", "source": ["state", "county"]},
        ]
    ),
    "vtd": Geography(
        geog="vtd", name="vtd", descrip="Voting District (VTD)", shp="vtd", cvap=None, level="700", geoid_len=11,
        states=[],
        indices="""
            CREATE INDEX IF NOT EXISTS idx_vtd{dec_yy}_vtd ON vtd{dec_yy} (statefp, countyfp, vtdst);
            CREATE INDEX IF NOT EXISTS idx_vtd{dec_yy}_county_id ON vtd{dec_yy} (countyid);
            CREATE INDEX IF NOT EXISTS idx_vtd{dec_yy}_name ON vtd{dec_yy} (name);
        """,
        fields=[
            {"field": "geoid",
                "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": []},
            {"field": "name", "type": "TEXT",
                "constraint": "NOT NULL", "source": []},
            {"field": "statefp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "state"]},
            {"field": "countyfp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "county"]},
            {"field": "vtdst", "type": "TEXT(10)", "constraint": "NOT NULL", "source": [
                "vtd"]},
            {"field": "vtdi", "type": "TEXT(10)", "constraint": "NOT NULL", "source": [
                "vtdi"]},
            {"field": "countyid", "type": "TEXT(15)",
                "constraint": "NOT NULL REFERENCES county{dec_yy} (geoid)", "source": ["state", "county"]},
        ]
    ),
    "c": Geography(
        geog="c", name="county", descrip="County", shp="county", cvap="County", level="050", geoid_len=5,
        states=[],
        indices="""
            CREATE INDEX IF NOT EXISTS idx_county_county{dec_yy} ON county{dec_yy} (statefp, countyfp);
            CREATE INDEX IF NOT EXISTS idx_county_name{dec_yy} ON county{dec_yy} (name);
        """,
        fields=[
            {"field": "geoid",
                "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": []},
            {"field": "statefp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "state"]},
            {"field": "countyfp", "type": "TEXT(5)", "constraint": "NOT NULL", "source": [
                "county"]},
            {"field": "name", "type": "TEXT",
                "constraint": "NOT NULL", "source": []},
        ]
    ),
    "st": Geography(
        geog="st", name="state", descrip="State", shp="state", cvap="State", level="040", geoid_len=2, indices="",
        states=[],
        fields=[
            {"field": "geoid",
                "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": []},
            {"field": "name", "type": "TEXT",
                "constraint": "NOT NULL", "source": []},
        ]
    ),
}
