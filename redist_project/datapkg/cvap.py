# -*- coding: utf-8 -*-
"""QGIS Redistricting Project Plugin - import cvap

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
import datetime
import logging
import pathlib
import sqlite3
import zipfile
from collections.abc import Callable
from email.message import Message
from email.utils import parsedate_to_datetime
from tempfile import mkdtemp

import numpy as np
import pandas as pd
import requests

from .geography import geographies
from .state import states
from .utils import spatialite_connect

categories = [
    "Total",
    "Not Hispanic or Latino",
    "American Indian or Alaska Native Alone",
    "Asian Alone",
    "Black or African American Alone",
    "Native Hawaiian or Other Pacific Islander Alone",
    "White Alone",
    "American Indian or Alaska Native and White",
    "Asian and White",
    "Black or African American and White",
    "American Indian or Alaska Native and Black or African American",
    "Remainder of Two or More Race Responses",
    "Hispanic or Latino",
]

col_names = {
    1: "total",
    2: "nonhispanic",
    3: "aiakn",
    4: "asian",
    5: "black",
    6: "hawpi",
    7: "white",
    8: "aiakn_white",
    9: "asian_white",
    10: "black_white",
    11: "black_aiakn",
    12: "other_multiracial",
    13: "hispanic",
}

combined_cols = {
    "ap_aiakn": ["aiakn", "aiakn_white", "black_aiakn"],
    "ap_black": ["black", "black_white", "black_aiakn"],
    "ap_asian": ["asian", "asian_white"]
}

totals = {
    "cvap_total": "vap_total",
    "cpop_total": "pop_total"
}

base_fields = {
    "cvap_aiakn": "vap_nh_aiakn",
    "cvap_asian": "vap_nh_asian",
    "cvap_black": "vap_nh_black",
    "cvap_hawpi": "vap_nh_hawpi",
    "cvap_white": "vap_nh_white",
    "cvap_aiakn_white": "vap_nh_aiakn_white",
    "cvap_asian_white": "vap_nh_asian_white",
    "cvap_black_white": "vap_nh_black_white",
    "cvap_black_aiakn": "vap_nh_black_aiakn",
    "cvap_other_multiracial": "vap_other_multiracial",
    "cvap_hispanic": "vap_hispanic",
    "cvap_nonhispanic": "vap_nonhispanic",
    "cpop_aiakn": "pop_nh_aiakn",
    "cpop_asian": "pop_nh_asian",
    "cpop_black": "pop_nh_black",
    "cpop_hawpi": "pop_nh_hawpi",
    "cpop_white": "pop_nh_white",
    "cpop_aiakn_white": "pop_nh_aiakn_white",
    "cpop_asian_white": "pop_nh_asian_white",
    "cpop_black_white": "pop_nh_black_white",
    "cpop_black_aiakn": "pop_nh_black_aiakn",
    "cpop_other_multiracial": "pop_other_multiracial",
    "cpop_hispanic": "pop_hispanic",
    "cpop_nonhispanic": "pop_nonhispanic",
}

# PL data reports has total multiracial
# CVAP data reports "other" multiracial - i.e., multiracial categories other than those reported separately
# meaning we need to subtract out the multiracial categories reported separately in the CVAP from
# the total multiracial to have a valid PL baseline for allocation of CVAP data
mr_subtract = ["{pop}_nh_black_aiakn", "{pop}_nh_aiakn_white",
               "{pop}_nh_black_white", "{pop}_nh_asian_white"]


def check_cache(cvap_url: str, cache_path: pathlib.Path):
    r = requests.head(cvap_url, allow_redirects=True, timeout=60)
    if r.ok:
        msg = Message()
        msg['content-disposition'] = r.headers.get('content-disposition')
        fname = msg.get_filename()

        if not fname:
            fname = cvap_url.rsplit('/', 1)[1]

        file_path: pathlib.Path = cache_path / fname
        if file_path.exists():
            if "last-modified" in r.headers:
                mod_date = parsedate_to_datetime(r.headers["last-modified"])
                if mod_date <= datetime.datetime.fromtimestamp(file_path.stat().st_ctime, tz=datetime.UTC):
                    return True, file_path

            file_path.unlink()

    return False, file_path


def download_cvap(cvap_url, file_path: pathlib.Path, progress: Callable[[float], None] = None):
    retries = 3
    while retries > 0:
        try:
            r = requests.get(cvap_url, allow_redirects=True, timeout=60, stream=True)
            if not r.ok:
                if r.status_code == 404:
                    return None
                else:
                    raise r.raise_for_status()

            total = int(r.headers.get("content-length", 0))
            count = 0
            block_size = 4096
            with file_path.open("wb+") as file:
                for data in r.iter_content(block_size):
                    if total:
                        count += len(data)
                    else:
                        count += 1
                    if progress:
                        progress(min(100, 100 * count / total) if total else min(count, 100))
                    file.write(data)
        except TimeoutError:
            retries -= 1
            if retries == 0:
                raise
            continue

        break

    with zipfile.ZipFile(file_path, "r") as z:
        z.extractall(file_path.parent)

    return file_path.parent


def load_cvap(st_fips, path: pathlib.Path):
    st_prefix = fr"^\d\d\d0000US{st_fips}"

    try:
        iter_csv = pd.read_csv(path, header=0, iterator=True, chunksize=1000)
        cvap = pd.concat([chunk[chunk["geoid"].str.match(st_prefix)]
                         for chunk in iter_csv])
        # cvap = pd.read_csv(path, header=0)
    except UnicodeDecodeError:
        iter_csv = pd.read_csv(
            path, header=0, encoding='latin-1', iterator=True, chunksize=1000)
        cvap = pd.concat([chunk[chunk["geoid"].str.match(st_prefix)]
                         for chunk in iter_csv])
        # cvap = pd.read_csv(path, header=0, encoding='latin-1')

    # drop US prefix from geoid
    cvap.geoid = cvap.geoid.str[9:]

    # drop unused columns
    cvap.drop(columns=["geoname", "lntitle",
              "cit_moe", "cvap_moe"], inplace=True)

    # rename population category columns
    cvap.rename(columns={"cit_est": "cpop", "cvap_est": "cvap"}, inplace=True)

    # pivot the race/ethnicity categories
    cvap = cvap.pivot(index="geoid", columns="lnnumber",
                      values=["cpop", "cvap"])

    # rename race/ethnicity columns from numbers to names
    cvap.rename(columns=col_names, level=1, inplace=True)

    # combine column names
    cvap.columns = ['_'.join(col) for col in cvap.columns.values]

    return cvap


def read_block_cvap(db, dec_year):
    table = f"{geographies['b'].name}{dec_year[-2:]}"
    fields = ["geoid", "vtdid", "cousubid", "aiannhid", "concityid",
              *totals.keys(), *base_fields.keys()]
    fields.extend(f"cvap_{f}" for f in combined_cols)
    fields.extend(f"cpop_{f}" for f in combined_cols)
    return pd.read_sql(f"SELECT {','.join(fields)} FROM {table} ORDER BY geoid", db, index_col="geoid")


def add_fields(cvap: pd.DataFrame):
    for p in ("cpop", "cvap"):
        for col, source in combined_cols.items():
            cvap[f"{p}_{col}"] = cvap[[f"{p}_{f}" for f in source]].sum(axis=1)

    pct_vap_df = cvap[list(base_fields.keys())[:12] + [f"cvap_{f}" for f in combined_cols.keys()]] \
        .div(cvap['cvap_total'], axis=0) \
        .rename(columns=lambda x: f"pct_{x}") \
        .replace(np.NaN, None)
    pct_pop_df = cvap[list(base_fields.keys())[12:] + [f"cpop_{f}" for f in combined_cols.keys()]] \
        .div(cvap['cpop_total'], axis=0) \
        .rename(columns=lambda x: f"pct_{x}") \
        .replace(np.NaN, None)

    return cvap.join([pct_vap_df, pct_pop_df])


def aggregate_cvap(geog: str, block_cvap: pd.DataFrame):
    id_field = f"{geographies[geog].name}id"
    return block_cvap.drop(columns={'vtdid', 'cousubid', 'aiannhid', 'concityid'} - {id_field}).groupby(id_field).sum()


def disaggregate_cvap(gpkg, geog, dec_year, cvap: pd.DataFrame, progress: Callable[[float], None] = None, prog_inc: int = 20):
    table = f"{geographies[geog].name}{dec_year[-2:]}"
    with spatialite_connect(gpkg) as db:
        pl = pd.read_sql_query(f"select * from {table} order by geoid", db).drop(columns="geom")

    # compute base fields for CVAP multiracial category
    pl['pop_other_multiracial'] = pl["pop_nh_multiracial"] - \
        pl[[f.format(pop='pop') for f in mr_subtract]].sum(axis=1)
    pl['vap_other_multiracial'] = pl["vap_nh_multiracial"] - \
        pl[[f.format(pop='vap') for f in mr_subtract]].sum(axis=1)

    fields = ["blkgrpid", *totals.values(), *base_fields.values()]
    pl_bg = pl[fields].groupby('blkgrpid').agg({f: "sum" for f in fields[1:]} | {
        "blkgrpid": "count"}).rename(columns={"blkgrpid": "COUNT"})
    pl = pl.join(pl_bg.add_suffix("_bg"), how="left", on="blkgrpid")
    pl = pl.join(cvap.add_suffix("_bg"), how="left", on="blkgrpid")

    new_cols = {
        "geoid": pl["geoid"].copy(),
        "vtdid": pl["vtdid"].copy(),
        "cousubid": pl["cousubid"].copy(),
        "aiannhid": pl["aiannhid"].copy(),
        "concityid": pl["concityid"].copy(),
    }
    total = len(totals) + len(base_fields)
    inc = prog_inc/total
    # pylint: disable=cell-var-from-loop
    for col, base in totals.items():
        new_cols[col] = pl.apply(
            lambda r: r[f"{col}_bg"] * r[base]/r[f"{base}_bg"]
            if r[f"{base}_bg"] != 0
            else r[f"{col}_bg"] / r["COUNT_bg"],
            axis=1
        )
        if progress:
            progress(inc)

    for col, base in base_fields.items():
        new_cols[col] = pl.apply(
            lambda r: r[f"{col}_bg"] * r[base]/r[f"{base}_bg"]
            if r[f"{base}_bg"] != 0
            else r[f"{col}_bg"] * r[f"{base[:3]}_total"] / r[f"{base[:3]}_total_bg"]
            if r[f"{base[:3]}_total_bg"] != 0
            else r[f"{col}_bg"] / r["COUNT_bg"],
            axis=1
        )
        if progress:
            progress(inc)
    # pylint: enable=cell-var-from-loop

    cvap_df = pd.DataFrame.from_dict(new_cols)
    cvap_df.set_index('geoid', inplace=True)

    return add_fields(cvap_df)


def add_cvap_data_to_geog(db: sqlite3.Connection, geog, dec_year, geog_cvap: pd.DataFrame):
    fields = [*totals.keys(), *base_fields.keys()]
    fields.extend(f"cvap_{f}" for f in combined_cols)
    fields.extend(f"cpop_{f}" for f in combined_cols)
    fields.extend(f"pct_{f}" for f in base_fields.keys())
    fields.extend(f"pct_cvap_{f}" for f in combined_cols)
    fields.extend(f"pct_cpop_{f}" for f in combined_cols)
    table = f"{geographies[geog].name}{dec_year[-2:]}"

    sql = ";".join(f"ALTER TABLE {table} ADD COLUMN {f} REAL" for f in fields)
    db.executescript(sql)

    sql = f"UPDATE {table} SET {', '.join(f'{f} = ?{n+2}' for n, f in enumerate(fields))} WHERE geoid = ?1"
    db.executemany(sql, geog_cvap.itertuples())


def check_table_exists(db: sqlite3.Connection, geog, dec_year):
    table = f"{geographies[geog].name}{dec_year[-2:]}"
    r = db.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND tbl_name='{table}'")
    return r.fetchone() is not None


def check_cvap_cols_exist(db: sqlite3.Connection, geog, dec_year):
    table = f"{geographies[geog].name}{dec_year[-2:]}"
    schema = pd.read_sql_query(
        f"PRAGMA table_info('{table}')", db, index_col="name")
    return "cvap_total" in schema.index


def add_cvap_data_to_gpkg(
    gpkg_name,
    state: str,
    dec_year: str,
    cvap_year: str,
    src_path=None,
    prog_cb: Callable[[float], None] = None
):
    def dl_prog(p: float):
        if prog_cb:
            prog_cb(0.15 * p)

    def progress(n):
        if prog_cb:
            nonlocal count
            count += n
            prog_cb(100 * count/total)

    if src_path is None:
        src_path = pathlib.Path(mkdtemp())

    cvap_url = 'https://www2.census.gov/programs-surveys/decennial/rdo/datasets/' \
        f'{cvap_year}/{cvap_year}-cvap/CVAP_{int(cvap_year)-4}-{cvap_year}_ACS_csv_files.zip'
    cached, file_path = check_cache(cvap_url, src_path)
    if not cached:
        logging.info("Downloading %s CVAP data for %s", cvap_year, states[state].name)
        if not download_cvap(cvap_url, file_path, dl_prog):
            return False
        total = 100
        count = 15
    else:
        logging.info("Using cached %s CVAP data for %s", cvap_year, states[state].name)
        total = 85
        count = 0

    geog_cvap = None
    block_cvap = None

    with spatialite_connect(gpkg_name) as db:
        # first do blocks from blockgroups
        if not check_cvap_cols_exist(db, "b", dec_year):
            logging.info("Loading block group CVAP data")
            geog_cvap = load_cvap(states[state].fips, src_path / "BlockGr.csv")
            logging.info("Disaggregating block group CVAP data to census blocks")
            block_cvap = disaggregate_cvap(gpkg_name, "b", dec_year, geog_cvap, progress)
            logging.info("Adding CVAP columns to census blocks")
            add_cvap_data_to_geog(db, "b", dec_year, block_cvap.drop(
                columns=["vtdid", "cousubid", "aiannhid", "concityid"]))
            # drop pct columns before aggregating to other levels
            block_cvap.drop(columns=block_cvap.filter(
                regex="pct_").columns, inplace=True)
        else:
            logging.info("CVAP data already present in census block table")

        # then do other geographies
        inc = (total - count) // \
            sum(1 for g in geographies.values()
                if g.geog != "b" and (not g.states or state in g.states) and check_table_exists(db, g.geog, dec_year))
        for g, geog in geographies.items():
            if g == "b":
                continue

            if not check_table_exists(db, g, dec_year):
                logging.info("%s table does not exist...skipping", geog.descrip)
                continue

            if check_cvap_cols_exist(db, g, dec_year):
                logging.info("CVAP data already present in %s table", geog.descrip)
                progress(inc)
                continue

            if geog.cvap is None:
                logging.info("Aggregating CVAP data to %s", geog.name)
                if block_cvap is None:
                    block_cvap = read_block_cvap(db, dec_year)
                geog_cvap = aggregate_cvap(g, block_cvap)
            elif g != "bg" or geog_cvap is None:
                logging.info("Loading %s CVAP data", geog.name)
                geog_cvap = load_cvap(states[state].fips, src_path / f"{geog.cvap}.csv")

            geog_cvap = add_fields(geog_cvap)
            logging.info("Adding CVAP columns to %s for %s", geog.name, states[state].name)
            add_cvap_data_to_geog(db, g, dec_year, geog_cvap)
            progress(inc)

    return True
