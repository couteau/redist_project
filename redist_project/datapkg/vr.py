"""QGIS Redistricting Project Plugin - import voter data

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
import pathlib
import re
from collections.abc import (
    Callable,
    Iterator
)
from datetime import datetime
from itertools import islice

import pandas as pd

from .utils import spatialite_connect

vr_fields = [
    {'field': 'reg_party_democrat', 'source': ['party_dem']},
    {'field': 'reg_party_republican', 'source': ['party_rep']},
    {'field': 'reg_party_no_party', 'source': ['party_npp']},
    {'field': 'reg_party_other', 'source': ['party_oth']},
    {'field': 'reg_party_unknown', 'source': ['party_unk']},
    {'field': 'reg_white', 'source': [
        'eth2_euro', 'eth2_34', 'eth2_61', 'eth2_66']},
    {'field': 'reg_hispanic', 'source': ['eth2_64']},
    {'field': 'reg_black', 'source': ['eth2_93', 'eth2_99']},
    {'field': 'reg_asian', 'source': [
        'eth2_10', 'eth2_23', 'eth2_14', 'eth2_12', 'eth2_21', 'eth2_85']},
    {'field': 'reg_mena', 'source': ['eth2_30', 'eth2_33', 'eth2_32']},
    {'field': 'reg_aiakn', 'source': ['eth2_81']},
    {'field': 'reg_race_unknown', 'source': ['eth2_unk']}
]


def add_vr_to_block(gpkg: pathlib.Path, dec_year: str, vr_file: pathlib.Path, progress: Callable[[float], None] = None):
    dec_yy = dec_year[-2:]
    if not vr_file.exists():
        return False

    vr_data = pd.read_csv(vr_file, index_col=f"geoid{dec_yy}")
    cols = {"reg_total": vr_data["total_reg"]}
    for f in vr_fields:
        if len(f["source"]) == 1:
            if f["source"][0] in vr_data.columns:
                cols[f["field"]] = vr_data[f["source"][0]]
                cols[f"pct_{f['field']}"] = cols[f["field"]] / \
                    vr_data["total_reg"]
        else:
            flds = [fld for fld in f["source"] if fld in vr_data.columns]
            if flds:
                cols[f["field"]] = vr_data[flds].sum(axis=1)
                cols[f"pct_{f['field']}"] = cols[f["field"]] / \
                    vr_data["total_reg"]

    df = pd.DataFrame(cols)

    with spatialite_connect(gpkg) as db:
        sql = f"""
            ALTER TABLE block{dec_yy} ADD COLUMN reg_total INTEGER;
            ALTER TABLE block{dec_yy} ADD COLUMN reg_party_democrat INTEGER;
            ALTER TABLE block{dec_yy} ADD COLUMN reg_party_republican INTEGER;
            ALTER TABLE block{dec_yy} ADD COLUMN reg_party_no_party INTEGER;
            ALTER TABLE block{dec_yy} ADD COLUMN reg_party_other INTEGER;
            ALTER TABLE block{dec_yy} ADD COLUMN reg_party_unknown INTEGER;
            ALTER TABLE block{dec_yy} ADD COLUMN reg_white INTEGER; --eth2_euro + eth2_34
            ALTER TABLE block{dec_yy} ADD COLUMN reg_hispanic INTEGER; --eth2__64
            ALTER TABLE block{dec_yy} ADD COLUMN reg_black INTEGER; --eth2_93 + eth2_99
            ALTER TABLE block{dec_yy} ADD COLUMN reg_asian INTEGER; --eth2_10 + eth2+23 + eth2_14 + eth2_12 + eth2_21
            ALTER TABLE block{dec_yy} ADD COLUMN reg_mena INTEGER; --eth2_30 + eth2_33 + eth2_32
            ALTER TABLE block{dec_yy} ADD COLUMN reg_aiakn INTEGER; --eth2_81
            ALTER TABLE block{dec_yy} ADD COLUMN reg_race_unknown INTEGER; --eth2_unk
            ALTER TABLE block{dec_yy} ADD COLUMN pct_reg_party_democrat REAL;
            ALTER TABLE block{dec_yy} ADD COLUMN pct_reg_party_republican REAL;
            ALTER TABLE block{dec_yy} ADD COLUMN pct_reg_party_no_party REAL;
            ALTER TABLE block{dec_yy} ADD COLUMN pct_reg_party_other REAL;
            ALTER TABLE block{dec_yy} ADD COLUMN pct_reg_party_unknown REAL;
            ALTER TABLE block{dec_yy} ADD COLUMN pct_reg_white REAL; --eth2_euro + eth2_34
            ALTER TABLE block{dec_yy} ADD COLUMN pct_reg_hispanic REAL; --eth2__64
            ALTER TABLE block{dec_yy} ADD COLUMN pct_reg_black REAL; --eth2_93 + eth2_99
            ALTER TABLE block{dec_yy} ADD COLUMN pct_reg_asian REAL; --eth2_10 + eth2+23 + eth2_14 + eth2_12 + eth2_21
            ALTER TABLE block{dec_yy} ADD COLUMN pct_reg_mena REAL; --eth2_30 + eth2_33 + eth2_32
            ALTER TABLE block{dec_yy} ADD COLUMN pct_reg_aiakn REAL; --eth2_81
            ALTER TABLE block{dec_yy} ADD COLUMN pct_reg_race_unknown REAL; --eth2_unk
            """

        db.executescript(sql)

        sql = f"UPDATE block{dec_yy} " \
            f"SET {', '.join(f'{f} = ?{n+2}' for n, f in enumerate(df.columns))} " \
            "WHERE geoid = ?1"

        total = len(df)
        count = 0
        records: Iterator[tuple] = df.itertuples()
        chunk_size = total // 9
        last_chunk = total % 9
        for _ in range(9):
            f = islice(records, chunk_size)
            db.executemany(sql, f)
            count += chunk_size
            if progress:
                progress(100 * count / total)
        if last_chunk:
            f = islice(records, last_chunk)
            db.executemany(sql, f)
            count += last_chunk
        if progress:
            progress(100 * count / total)

    return True


def validate_vr(filename, st: str, dec_year):
    pat = r"([A-Z]{2})_l2_(20[1-3]0)block_agg_(\d{8}).csv"
    if not (r := re.search(pat, filename)):
        return ValueError("Invalid voter file name")

    if r[1] != st.upper():
        return ValueError("Voter file does not match state")

    if r[2] != dec_year:
        return ValueError("Voter file decennial year does not match GeoPackage")

    try:
        datetime.strptime(r[3], "%Y%m%d")
    except ValueError as e:
        return e

    return True
