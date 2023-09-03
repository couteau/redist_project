# -*- coding: utf-8 -*-
"""Redistricting Project Generator 

    SQL queries


        begin                : 2022-01-15
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Cryptodira
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

import sys
from string import Template

module = sys.modules[__name__]

PL_TABLES = {
    'block': 'b',
    'vtd': 'vtd',
    'county': 'cnty',
    'place': 'place'
}

CVAP_TABLES = {
    'block': '{dec_year}_b',
    'vtd': 'vtd',
    'county': 'cnty',
    'place': 'place'
}

GEOID_LEN = {
    'block': 15,
    'vtd': 11,
    'county': 5,
    'place': 7
}

pop_fields = [
    {"field": "pop_total", "type": "INTEGER", "source": "p0010001", "total": ""},
    {"field": "pop_white", "type": "INTEGER",
        "source": "p0010003", "total": "p0010001"},
    {"field": "pop_black", "type": "INTEGER",
        "source": "p0010004", "total": "p0010001"},
    {"field": "pop_apblack", "type": "INTEGER", "source": "p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071", "total": "p0010001"},
    {"field": "pop_amind_aknative", "type": "INTEGER",
        "source": "p0010005", "total": "p0010001"},
    {"field": "pop_apamind_aknative", "type": "INTEGER", "source": "p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071", "total": "p0010001"},
    {"field": "pop_asian", "type": "INTEGER",
        "source": "p0010006", "total": "p0010001"},
    {"field": "pop_apasian", "type": "INTEGER", "source": "p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071", "total": "p0010001"},
    {"field": "pop_hawaii_pi", "type": "INTEGER",
        "source": "p0010007", "total": "p0010001"},
    {"field": "pop_aphawaii_pi", "type": "INTEGER", "source": "p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071", "total": "p0010001"},
    {"field": "pop_other_single_race", "type": "INTEGER",
        "source": "p0010008", "total": "p0010001"},
    {"field": "pop_multiracial", "type": "INTEGER",
        "source": "p0010009", "total": "p0010001"},
    {"field": "pop_hispanic", "type": "INTEGER",
        "source": "p0020002", "total": "p0020001"},
    {"field": "pop_nh_white", "type": "INTEGER",
        "source": "p0020005", "total": "p0020001"},
    {"field": "pop_nh_black", "type": "INTEGER",
        "source": "p0020006", "total": "p0020001"},
    {"field": "pop_nh_apblack", "type": "INTEGER", "source": "p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073", "total": "p0020001"},
    {"field": "pop_nh_amind_aknative", "type": "INTEGER",
        "source": "p0020007", "total": "p0020001"},
    {"field": "pop_nh_apamind_aknative", "type": "INTEGER", "source": "p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073", "total": "p0020001"},
    {"field": "pop_nh_asian", "type": "INTEGER",
        "source": "p0020008", "total": "p0020001"},
    {"field": "pop_nh_apasian", "type": "INTEGER", "source": "p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073", "total": "p0020001"},
    {"field": "pop_hn_hawaii_pi", "type": "INTEGER",
        "source": "p0020009", "total": "p0020001"},
    {"field": "pop_nh_aphawaii_pi", "type": "INTEGER", "source": "p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073", "total": "p0020001"},
    {"field": "pop_nh_other_single_race", "type": "INTEGER",
        "source": "p0020010", "total": "p0020001"},
    {"field": "pop_nh_multiracial", "type": "INTEGER",
        "source": "p0020011", "total": "p0020001"},
    {"field": "vap_total", "type": "INTEGER", "source": "p0030001", "total": ""},
    {"field": "vap_white", "type": "INTEGER",
        "source": "p0030003", "total": "p0030001"},
    {"field": "vap_black", "type": "INTEGER",
        "source": "p0030004", "total": "p0030001"},
    {"field": "vap_apblack", "type": "INTEGER", "source": "p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071", "total": "p0030001"},
    {"field": "vap_multiracial_black", "type": "INTEGER", "source": "p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071", "total": "p0030001"},
    {"field": "vap_black_black_white", "type": "INTEGER",
        "source": "p0030004 + P0030011", "total": "p0030001"},
    {"field": "vap_amind_aknative", "type": "INTEGER",
        "source": "p0030005", "total": "p0030001"},
    {"field": "vap_apamind_aknative", "type": "INTEGER", "source": "p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071", "total": "p0030001"},
    {"field": "vap_asian", "type": "INTEGER",
        "source": "p0030006", "total": "p0030001"},
    {"field": "vap_apasian", "type": "INTEGER", "source": "p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071", "total": "p0030001"},
    {"field": "vap_hawaii_pi", "type": "INTEGER",
        "source": "p0030007", "total": "p0030001"},
    {"field": "vap_aphawaii_pi", "type": "INTEGER", "source": "p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071", "total": "p0030001"},
    {"field": "vap_other_single_race", "type": "INTEGER",
        "source": "p0030008", "total": "p0030001"},
    {"field": "vap_multiracial", "type": "INTEGER",
        "source": "p0030009", "total": "p0030001"},
    {"field": "vap_hispanic", "type": "INTEGER",
        "source": "p0040002", "total": "p0040001"},
    {"field": "vap_nh_white", "type": "INTEGER",
        "source": "p0040005", "total": "p0040001"},
    {"field": "vap_nh_black", "type": "INTEGER",
        "source": "p0040006", "total": "p0040001"},
    {"field": "vap_nh_apblack", "type": "INTEGER", "source": "p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073", "total": "p0040001"},
    {"field": "vap_nh_dojblack", "type": "INTEGER",
        "source": "p0040006 + p0040013", "total": "p0040001"},
    {"field": "vap_nh_multiracial_black", "type": "INTEGER", "source": "p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073", "total": "p0040001"},
    {"field": "vap_nh_amind_aknative", "type": "INTEGER",
        "source": "p0040007", "total": "p0040001"},
    {"field": "vap_nh_apamind_aknative", "type": "INTEGER", "source": "p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073", "total": "p0040001"},
    {"field": "vap_nh_asian", "type": "INTEGER",
        "source": "p0040008", "total": "p0040001"},
    {"field": "vap_nh_apasian", "type": "INTEGER", "source": "p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073", "total": "p0040001"},
    {"field": "vap_nh_hawaii_pi", "type": "INTEGER",
        "source": "p0040009", "total": "p0040001"},
    {"field": "vap_nh_aphawaii_pi", "type": "INTEGER", "source": "p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073", "total": "p0040001"},
    {"field": "vap_nh_other_single_race", "type": "INTEGER",
        "source": "p0040010", "total": "p0040001"},
    {"field": "vap_nh_multiracial", "type": "INTEGER",
        "source": "p0040011", "total": "p0040001"},
    {"field": "pop_group_quarters_total", "type": "INTEGER",
        "source": "p0050001", "total": "p0010001"},
    {"field": "pop_correctional", "type": "INTEGER",
        "source": "p0050003", "total": "p0010001"},
    {"field": "pop_juvenile", "type": "INTEGER",
        "source": "p0050004", "total": "p0010001"},
    {"field": "pop_nursing", "type": "INTEGER",
        "source": "p0050005", "total": "p0010001"},
    {"field": "pop_other_inst", "type": "INTEGER",
        "source": "p0050006", "total": "p0010001"},
    {"field": "pop_university", "type": "INTEGER",
        "source": "p0050008", "total": "p0010001"},
    {"field": "pop_military", "type": "INTEGER",
        "source": "p0050009", "total": "p0010001"},
    {"field": "pop_other_noninst", "type": "INTEGER",
        "source": "p0050010", "total": "p0010001"},
]

create_pop_fields = ",\n".join(
    f'{p["field"]} {p["type"]}' for p in pop_fields
)
create_pct_fields = ',\n'.join(
    f'pct_{f["field"]} REAL' for f in pop_fields if f["total"]
)
insert_pop_fields = ','.join(f["field"] for f in pop_fields)
insert_pct_fields = ','.join(
    f'pct_{f["field"]}' for f in pop_fields if f["total"]
)
src_pop_fields = ','.join(
    f'{f["source"]} AS {f["field"]}' for f in pop_fields
)
src_pct_fields = ','.join(
    f'CAST({f["source"]} AS REAL) / NULLIF({f["total"]}, 0) AS pct_{f["field"]}' for f in pop_fields if f["total"]
)


def create_table_script(table, year):
    dec_yy = year[2:]
    fields = getattr(module, f'{table}_fields')
    create_table_fields = ",\n" \
        .join(f'{f["field"]} {f["type"]} {f["constraint"]}'.strip() for f in fields) \
        .format(dec_yyyy=year, dec_yy=dec_yy)
    create_indices = getattr(module, f'create_{table}_indices').format(
        dec_yyyy=year, dec_yy=dec_yy)

    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table}{dec_yy} (fid INTEGER NOT NULL PRIMARY KEY,\n{create_table_fields},\n{create_pop_fields},\n{create_pct_fields});"
    make_spatial_sql = f"""
        SELECT gpkgAddGeometryColumn("{table}{dec_yy}", "geom", "MULTIPOLYGON", 0, 0, (SELECT srs_id FROM gpkg_geometry_columns WHERE table_name="pl{year}_{PL_TABLES[table]}"));
        SELECT gpkgAddGeometryTriggers("{table}{dec_yy}", "geom");
        SELECT gpkgAddSpatialIndex("{table}{dec_yy}", "geom");
    """

    return f"{create_table_sql}\n{make_spatial_sql}\n{create_indices}"


def insert_data_script(table, year):
    dec_yy = year[2:]
    pl_table = f'pl{year}_{PL_TABLES[table]}'
    fields = getattr(module, f'{table}_fields')
    insert_table_fields = "," \
        .join(f["field"] for f in fields) \
        .format(dec_yy=dec_yy)
    src_table_fields = ',' \
        .join(f'{f["source"]}' for f in fields) \
        .format(dec_yy=dec_yy)
    source_query = f"SELECT fid, {src_table_fields}, {src_pop_fields}, {src_pct_fields}, geom FROM {pl_table};"
    return f"INSERT INTO {table}{dec_yy} (fid, {insert_table_fields}, {insert_pop_fields}, {insert_pct_fields}, geom) {source_query}"


# County
county_fields = [
    {"field": "geoid",
        "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": "geoid{dec_yy}"},
    {"field": "statefp",
        "type": "TEXT(5)", "constraint": "NOT NULL", "source": "statefp{dec_yy}"},
    {"field": "countyfp",
        "type": "TEXT(5)", "constraint": "NOT NULL", "source": "countyfp{dec_yy}"},
    {"field": "name", "type": "TEXT",
        "constraint": "NOT NULL", "source": "name{dec_yy}"},
]

create_county_indices = """
    CREATE INDEX IF NOT EXISTS idx_county_county{dec_yy} ON county{dec_yy} (statefp, countyfp);
    CREATE INDEX IF NOT EXISTS idx_county_name{dec_yy} ON county{dec_yy} (name);
"""


create_county_sql = """
    CREATE TABLE IF NOT EXISTS county{dec_yy} (
        fid INTEGER NOT NULL PRIMARY KEY,
        geoid TEXT(15) NOT NULL UNIQUE,
        statefp TEXT(5) NOT NULL, --state fips
        countyfp TEXT(5) NOT NULL, --county fips
        name TEXT NOT NULL,
        pop_total INTEGER, --p0010001
        pop_white INTEGER, --p0010003
        pop_black INTEGER, --p0010004
        pop_apblack INTEGER, --p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071
        pop_amind_aknative INTEGER, --p0010005
        pop_apamind_aknative INTEGER, --p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071
        pop_asian INTEGER, --p0010006
        pop_apasian INTEGER, --p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071
        pop_hawaii_pi INTEGER, --p0010007
        pop_aphawaii_pi INTEGER, --p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071
        pop_other_single_race INTEGER, --p0010008
        pop_multiracial INTEGER, --p0010009
        pop_hispanic INTEGER, --p0020002
        pop_nh_white INTEGER, --p0020005
        pop_nh_black INTEGER, --p0020006
        pop_nh_apblack INTEGER, --p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073
        pop_nh_amind_aknative INTEGER, --p0020007
        pop_nh_apamind_aknative INTEGER, --p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073
        pop_nh_asian INTEGER, --p0020008
        pop_nh_apasian INTEGER, --p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073
        pop_hn_hawaii_pi INTEGER, --p0020009
        pop_nh_aphawaii_pi INTEGER, --p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073
        pop_nh_other_single_race INTEGER, --p0020010
        pop_nh_multiracial INTEGER, --p0020011
        vap_total INTEGER, --p0030001
        vap_white INTEGER, --p0030003
        vap_black INTEGER, --p0030004
        vap_apblack INTEGER, --p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071
        vap_multiracial_black INTEGER, --p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071
        vap_black_black_white INTEGER, --p0030004 + P0030011
        vap_amind_aknative INTEGER, --p0030005
        vap_apamind_aknative INTEGER, --p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071
        vap_asian INTEGER, --p0030006
        vap_apasian INTEGER, --p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071
        vap_hawaii_pi INTEGER, --p0030007
        vap_aphawaii_pi INTEGER, --p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071
        vap_other_single_race INTEGER, --p0030008
        vap_multiracial INTEGER, --p0030009
        vap_hispanic INTEGER, --p0040002
        vap_nh_white INTEGER, --p0040005
        vap_nh_black INTEGER, --p0040006
        vap_nh_apblack INTEGER, --p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073
        vap_nh_dojblack INTEGER, --p0040006 + p0040013
        vap_nh_multiracial_black INTEGER, --p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073
        vap_nh_amind_aknative INTEGER, --p0040007
        vap_nh_apamind_aknative INTEGER, --p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073
        vap_nh_asian INTEGER, --p0040008
        vap_nh_apasian INTEGER, --p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073
        vap_nh_hawaii_pi INTEGER, --p0040009
        vap_nh_aphawaii_pi INTEGER, --p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073
        vap_nh_other_single_race INTEGER, --p0040010
        vap_nh_multiracial INTEGER, --p0040011
        pop_group_quarters_total INTEGER, --p0050001
        pop_correctional INTEGER, --p0050003
        pop_juvenile INTEGER, --p0050004
        pop_nursing INTEGER, --p0050005
        pop_other_inst INTEGER, --p0050006
        pop_university INTEGER, --p0050008
        pop_military INTEGER, --p0050009
        pop_other_noninst INTEGER, --p0050010
        pct_pop_white REAL,
        pct_pop_black REAL,
        pct_pop_apblack REAL,
        pct_pop_amind_aknative REAL,
        pct_pop_apamind_aknative REAL,
        pct_pop_asian REAL,
        pct_pop_apasian REAL,
        pct_pop_hawaii_pi REAL,
        pct_pop_aphawaii_pi REAL,
        pct_pop_other_single_race REAL,
        pct_pop_multiracial REAL,
        pct_pop_hispanic REAL,
        pct_pop_nh_white REAL,
        pct_pop_nh_black REAL,
        pct_pop_nh_apblack REAL,
        pct_pop_nh_amind_aknative REAL,
        pct_pop_nh_apamind_aknative REAL,
        pct_pop_nh_asian REAL,
        pct_pop_nh_apasian REAL,
        pct_pop_hn_hawaii_pi REAL,
        pct_pop_hn_aphawaii_pi REAL,
        pct_pop_nh_other_single_race REAL,
        pct_pop_nh_multiracial REAL,
        pct_vap_white REAL,
        pct_vap_black REAL,
        pct_vap_apblack REAL,
        pct_vap_amind_aknative REAL,
        pct_vap_apamind_aknative REAL,
        pct_vap_asian REAL,
        pct_vap_apasian REAL,
        pct_vap_hawaii_pi REAL,
        pct_vap_aphawaii_pi REAL,
        pct_vap_other_single_race REAL,
        pct_vap_multiracial REAL,
        pct_vap_hispanic REAL,
        pct_vap_nh_white REAL,
        pct_vap_nh_black REAL,
        pct_vap_nh_apblack REAL,
        pct_vap_nh_amind_aknative REAL,
        pct_vap_nh_apamind_aknative REAL,
        pct_vap_nh_asian REAL,
        pct_vap_nh_apasian REAL,
        pct_vap_nh_hawaii_pi REAL,
        pct_vap_nh_aphawaii_pi REAL,
        pct_vap_nh_other_single_race REAL,
        pct_vap_nh_multiracial REAL,
        pct_pop_group_quarters_total REAL,
        pct_pop_correctional REAL,
        pct_pop_juvenile REAL,
        pct_pop_nursing REAL,
        pct_pop_other_inst REAL,
        pct_pop_university REAL,
        pct_pop_military REAL,
        pct_pop_other_noninst REAL
    );
    SELECT gpkgAddGeometryColumn("county{dec_yy}", "geom", "MULTIPOLYGON", 0, 0, (SELECT srs_id FROM gpkg_geometry_columns WHERE table_name="pl{dec_yyyy}_cnty"));
    SELECT gpkgAddGeometryTriggers("county{dec_yy}", "geom");
    SELECT gpkgAddSpatialIndex("county{dec_yy}", "geom");
    CREATE INDEX IF NOT EXISTS idx_county_county{dec_yy} ON county{dec_yy} (statefp, countyfp);
    CREATE INDEX IF NOT EXISTS idx_county_name{dec_yy} ON county{dec_yy} (name);
    """

vtd_fields = [
    {"field": "geoid",
        "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": "geoid{dec_yy}"},
    {"field": "name", "type": "TEXT",
        "constraint": "NOT NULL", "source": "name{dec_yy}"},
    {"field": "statefp",
        "type": "TEXT(5)", "constraint": "NOT NULL", "source": "statefp{dec_yy}"},
    {"field": "countyfp",
        "type": "TEXT(5)", "constraint": "NOT NULL", "source": "countyfp{dec_yy}"},
    {"field": "vtdst",
        "type": "TEXT(10)", "constraint": "NOT NULL", "source": "vtdst{dec_yy}"},
    {"field": "vtdi",
        "type": "TEXT(10)", "constraint": "NOT NULL", "source": "vtdi{dec_yy}"},
    {"field": "countyid",
        "type": "TEXT(15)", "constraint": "NOT NULL REFERENCES county{dec_yy} (geoid)", "source": ""},
]

create_vtd_indices = """
    CREATE INDEX IF NOT EXISTS idx_vtd{dec_yy}_vtd ON vtd{dec_yy} (statefp, countyfp, vtdst);
    CREATE INDEX IF NOT EXISTS idx_vtd{dec_yy}_county_id ON vtd{dec_yy} (countyid);
    CREATE INDEX IF NOT EXISTS idx_vtd{dec_yy}_name ON vtd{dec_yy} (name);
"""

# VTD
create_vtd_sql = """
    CREATE TABLE IF NOT EXISTS vtd{dec_yy} (
        fid integer NOT NULL PRIMARY KEY,
        geoid TEXT(15) NOT NULL UNIQUE,
        name TEXT NOT NULL,
        statefp TEXT(5) NOT NULL,
        countyfp TEXT(5) NOT NULL,
        vtdst TEXT(10) NOT NULL,
        vtdi TEXT(10) NOT NULL,
        countyid TEXT(15) NOT NULL REFERENCES county{dec_yy} (geoid),
        pop_total INTEGER, --p0010001
        pop_white INTEGER, --p0010003
        pop_black INTEGER, --p0010004
        pop_apblack INTEGER, --p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071
        pop_amind_aknative INTEGER, --p0010005
        pop_apamind_aknative INTEGER, --p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071
        pop_asian INTEGER, --p0010006
        pop_apasian INTEGER, --p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071
        pop_hawaii_pi INTEGER, --p0010007
        pop_aphawaii_pi INTEGER, --p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071
        pop_other_single_race INTEGER, --p0010008
        pop_multiracial INTEGER, --p0010009
        pop_hispanic INTEGER, --p0020002
        pop_nh_white INTEGER, --p0020005
        pop_nh_black INTEGER, --p0020006
        pop_nh_apblack INTEGER, --p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073
        pop_nh_amind_aknative INTEGER, --p0020007
        pop_nh_apamind_aknative INTEGER, --p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073
        pop_nh_asian INTEGER, --p0020008
        pop_nh_apasian INTEGER, --p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073
        pop_hn_hawaii_pi INTEGER, --p0020009
        pop_nh_aphawaii_pi INTEGER, --p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073
        pop_nh_other_single_race INTEGER, --p0020010
        pop_nh_multiracial INTEGER, --p0020011
        vap_total INTEGER, --p0030001
        vap_white INTEGER, --p0030003
        vap_black INTEGER, --p0030004
        vap_apblack INTEGER, --p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071
        vap_multiracial_black INTEGER, --p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071
        vap_black_black_white INTEGER, --p0030004 + P0030011
        vap_amind_aknative INTEGER, --p0030005
        vap_apamind_aknative INTEGER, --p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071
        vap_asian INTEGER, --p0030006
        vap_apasian INTEGER, --p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071
        vap_hawaii_pi INTEGER, --p0030007
        vap_aphawaii_pi INTEGER, --p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071
        vap_other_single_race INTEGER, --p0030008
        vap_multiracial INTEGER, --p0030009
        vap_hispanic INTEGER, --p0040002
        vap_nh_white INTEGER, --p0040005
        vap_nh_black INTEGER, --p0040006
        vap_nh_apblack INTEGER, --p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073
        vap_nh_dojblack INTEGER, --p0040006 + p0040013
        vap_nh_multiracial_black INTEGER, --p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073
        vap_nh_amind_aknative INTEGER, --p0040007
        vap_nh_apamind_aknative INTEGER, --p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073
        vap_nh_asian INTEGER, --p0040008
        vap_nh_apasian INTEGER, --p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073
        vap_nh_hawaii_pi INTEGER, --p0040009
        vap_nh_aphawaii_pi INTEGER, --p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073
        vap_nh_other_single_race INTEGER, --p0040010
        vap_nh_multiracial INTEGER, --p0040011
        pop_group_quarters_total INTEGER, --p0050001
        pop_correctional INTEGER, --p0050003
        pop_juvenile INTEGER, --p0050004
        pop_nursing INTEGER, --p0050005
        pop_other_inst INTEGER, --p0050006
        pop_university INTEGER, --p0050008
        pop_military INTEGER, --p0050009
        pop_other_noninst INTEGER, --p0050010
        pct_pop_white REAL,
        pct_pop_black REAL,
        pct_pop_apblack REAL,
        pct_pop_amind_aknative REAL,
        pct_pop_apamind_aknative REAL,
        pct_pop_asian REAL,
        pct_pop_apasian REAL,
        pct_pop_hawaii_pi REAL,
        pct_pop_aphawaii_pi REAL,
        pct_pop_other_single_race REAL,
        pct_pop_multiracial REAL,
        pct_pop_hispanic REAL,
        pct_pop_nh_white REAL,
        pct_pop_nh_black REAL,
        pct_pop_nh_apblack REAL,
        pct_pop_nh_amind_aknative REAL,
        pct_pop_nh_apamind_aknative REAL,
        pct_pop_nh_asian REAL,
        pct_pop_nh_apasian REAL,
        pct_pop_hn_hawaii_pi REAL,
        pct_pop_hn_aphawaii_pi REAL,
        pct_pop_nh_other_single_race REAL,
        pct_pop_nh_multiracial REAL,
        pct_vap_white REAL,
        pct_vap_black REAL,
        pct_vap_apblack REAL,
        pct_vap_amind_aknative REAL,
        pct_vap_apamind_aknative REAL,
        pct_vap_asian REAL,
        pct_vap_apasian REAL,
        pct_vap_hawaii_pi REAL,
        pct_vap_aphawaii_pi REAL,
        pct_vap_other_single_race REAL,
        pct_vap_multiracial REAL,
        pct_vap_hispanic REAL,
        pct_vap_nh_white REAL,
        pct_vap_nh_black REAL,
        pct_vap_nh_apblack REAL,
        pct_vap_nh_amind_aknative REAL,
        pct_vap_nh_apamind_aknative REAL,
        pct_vap_nh_asian REAL,
        pct_vap_nh_apasian REAL,
        pct_vap_nh_hawaii_pi REAL,
        pct_vap_nh_aphawaii_pi REAL,
        pct_vap_nh_other_single_race REAL,
        pct_vap_nh_multiracial REAL,
        pct_pop_group_quarters_total REAL,
        pct_pop_correctional REAL,
        pct_pop_juvenile REAL,
        pct_pop_nursing REAL,
        pct_pop_other_inst REAL,
        pct_pop_university REAL,
        pct_pop_military REAL,
        pct_pop_other_noninst REAL
    );
    SELECT gpkgAddGeometryColumn("vtd{dec_yy}", "geom", "MULTIPOLYGON", 0, 0, 4269);
    SELECT gpkgAddGeometryTriggers("vtd{dec_yy}", "geom");
    SELECT gpkgAddSpatialIndex("vtd{dec_yy}", "geom");
    CREATE INDEX IF NOT EXISTS idx_vtd{dec_yy}_vtd ON vtd{dec_yy} (statefp, countyfp, vtdst);
    CREATE INDEX IF NOT EXISTS idx_vtd{dec_yy}_county_id ON vtd{dec_yy} (countyid);
    CREATE INDEX IF NOT EXISTS idx_vtd{dec_yy}_name ON vtd{dec_yy} (name);
    """

# Census Block
block_fields = [
    {"field": "geoid",
        "type": "TEXT(15)", "constraint": "NOT NULL UNIQUE", "source": "geoid{dec_yy}"},
    {"field": "statefp",
        "type": "TEXT(5)", "constraint": "NOT NULL", "source": "statefp{dec_yy}"},
    {"field": "countyfp",
        "type": "TEXT(5)", "constraint": "NOT NULL", "source": "countyfp{dec_yy}"},
    {"field": "tractce",
        "type": "TEXT(10)", "constraint": "NOT NULL", "source": "tractce{dec_yy}"},
    {"field": "blockce",
        "type": "TEXT(10)", "constraint": "NOT NULL", "source": "blockce{dec_yy}"},
    {"field": "blkgrp",
        "type": "TEXT(5)", "constraint": "NOT NULL", "source": "blkgrp"},
    {"field": "vtd", "type": "TEXT(10)",
     "constraint": "NOT NULL", "source": "vtd"},
    {"field": "cousub", "type": "TEXT(10)",
     "constraint": "", "source": "cousub"},
    {"field": "place", "type": "TEXT(10)",
     "constraint": "", "source": "place"},
    {"field": "countyid", "type": "TEXT(15)", "constraint": "NOT NULL REFERENCES county{dec_yy} (geoid)",
     "source": "statefp{dec_yy} || countyfp{dec_yy}"},
    {"field": "tractid", "type": "TEXT(15)", "constraint": "NOT NULL",
     "source": "statefp{dec_yy} || countyfp{dec_yy} || tractce{dec_yy}"},
    {"field": "blkgrpid", "type": "TEXT(15)", "constraint": "NOT NULL",
     "source": "statefp{dec_yy} || countyfp{dec_yy} || tractce{dec_yy} || blkgrp"},
    {"field": "vtdid", "type": "TEXT(15)", "constraint": "NOT NULL REFERENCES vtd{dec_yy} (geoid)",
     "source": "statefp{dec_yy} || countyfp{dec_yy} || vtd"},
    {"field": "placeid", "type": "TEXT(15)", "constraint": "",
     "source": "statefp{dec_yy} || place as placeid"},
    {"field": "cousubid", "type": "TEXT(15)", "constraint": "",
     "source": "statefp{dec_yy} || countyfp{dec_yy} || cousub"},
]

create_block_indices = """
    CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_vtd ON block{dec_yy} (statefp, countyfp, vtd);
    CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_countyid ON block{dec_yy} (countyid);
    CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_vtdid ON block{dec_yy} (vtdid);
    CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_placeid ON block{dec_yy} (placeid);
    CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_cousubid ON block{dec_yy} (cousubid);
"""

create_block_sql = """
    CREATE TABLE IF NOT EXISTS block{dec_yy} (
        fid INTEGER NOT NULL PRIMARY KEY,
        geoid TEXT(15) NOT NULL UNIQUE,
        statefp TEXT(5) NOT NULL,
        countyfp TEXT(5) NOT NULL,
        tractce TEXT(10) NOT NULL,
        blockce TEXT(10) NOT NULL,
        blkgrp TEXT(5) NOT NULL,
        vtd TEXT(10) NOT NULL,
        cousub TEXT(10),
        place TEXT(10),
        countyid TEXT(15) NOT NULL REFERENCES county{dec_yy} (geoid),
        tractid TEXT(15) NOT NULL,
        blkgrpid TEXT(15) NOT NULL,
        vtdid TEXT (15) NOT NULL REFERENCES vtd{dec_yy} (geoid),
        placeid TEXT (15),
        cousubid TEXT(15),
        pop_total INTEGER, --p0010001
        pop_white INTEGER, --p0010003
        pop_black INTEGER, --p0010004
        pop_apblack INTEGER, --p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071
        pop_amind_aknative INTEGER, --p0010005
        pop_apamind_aknative INTEGER, --p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071
        pop_asian INTEGER, --p0010006
        pop_apasian INTEGER, --p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071
        pop_hawaii_pi INTEGER, --p0010007
        pop_aphawaii_pi INTEGER, --p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071
        pop_other_single_race INTEGER, --p0010008
        pop_multiracial INTEGER, --p0010009
        pop_hispanic INTEGER, --p0020002
        pop_nh_white INTEGER, --p0020005
        pop_nh_black INTEGER, --p0020006
        pop_nh_apblack INTEGER, --p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073
        pop_nh_amind_aknative INTEGER, --p0020007
        pop_nh_apamind_aknative INTEGER, --p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073
        pop_nh_asian INTEGER, --p0020008
        pop_nh_apasian INTEGER, --p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073
        pop_hn_hawaii_pi INTEGER, --p0020009
        pop_nh_aphawaii_pi INTEGER, --p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073
        pop_nh_other_single_race INTEGER, --p0020010
        pop_nh_multiracial INTEGER, --p0020011
        vap_total INTEGER, --p0030001
        vap_white INTEGER, --p0030003
        vap_black INTEGER, --p0030004
        vap_apblack INTEGER, --p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071
        vap_multiracial_black INTEGER, --p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071
        vap_black_black_white INTEGER, --p0030004 + P0030011
        vap_amind_aknative INTEGER, --p0030005
        vap_apamind_aknative INTEGER, --p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071
        vap_asian INTEGER, --p0030006
        vap_apasian INTEGER, --p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071
        vap_hawaii_pi INTEGER, --p0030007
        vap_aphawaii_pi INTEGER, --p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071
        vap_other_single_race INTEGER, --p0030008
        vap_multiracial INTEGER, --p0030009
        vap_hispanic INTEGER, --p0040002
        vap_nh_white INTEGER, --p0040005
        vap_nh_black INTEGER, --p0040006
        vap_nh_apblack INTEGER, --p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073
        vap_nh_dojblack INTEGER, --p0040006 + p0040013
        vap_nh_multiracial_black INTEGER, --p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073
        vap_nh_amind_aknative INTEGER, --p0040007
        vap_nh_apamind_aknative INTEGER, --p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073
        vap_nh_asian INTEGER, --p0040008
        vap_nh_apasian INTEGER, --p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073
        vap_nh_hawaii_pi INTEGER, --p0040009
        vap_nh_aphawaii_pi INTEGER, --p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073
        vap_nh_other_single_race INTEGER, --p0040010
        vap_nh_multiracial INTEGER, --p0040011
        pop_group_quarters_total INTEGER, --p0050001
        pop_correctional INTEGER, --p0050003
        pop_juvenile INTEGER, --p0050004
        pop_nursing INTEGER, --p0050005
        pop_other_inst INTEGER, --p0050006
        pop_university INTEGER, --p0050008
        pop_military INTEGER, --p0050009
        pop_other_noninst INTEGER, --p0050010
        pct_pop_white REAL,
        pct_pop_black REAL,
        pct_pop_apblack REAL,
        pct_pop_amind_aknative REAL,
        pct_pop_apamind_aknative REAL,
        pct_pop_asian REAL,
        pct_pop_apasian REAL,
        pct_pop_hawaii_pi REAL,
        pct_pop_aphawaii_pi REAL,
        pct_pop_other_single_race REAL,
        pct_pop_multiracial REAL,
        pct_pop_hispanic REAL,
        pct_pop_nh_white REAL,
        pct_pop_nh_black REAL,
        pct_pop_nh_apblack REAL,
        pct_pop_nh_amind_aknative REAL,
        pct_pop_nh_apamind_aknative REAL,
        pct_pop_nh_asian REAL,
        pct_pop_nh_apasian REAL,
        pct_pop_hn_hawaii_pi REAL,
        pct_pop_hn_aphawaii_pi REAL,
        pct_pop_nh_other_single_race REAL,
        pct_pop_nh_multiracial REAL,
        pct_vap_white REAL,
        pct_vap_black REAL,
        pct_vap_apblack REAL,
        pct_vap_amind_aknative REAL,
        pct_vap_apamind_aknative REAL,
        pct_vap_asian REAL,
        pct_vap_apasian REAL,
        pct_vap_hawaii_pi REAL,
        pct_vap_aphawaii_pi REAL,
        pct_vap_other_single_race REAL,
        pct_vap_multiracial REAL,
        pct_vap_hispanic REAL,
        pct_vap_nh_white REAL,
        pct_vap_nh_black REAL,
        pct_vap_nh_apblack REAL,
        pct_vap_nh_amind_aknative REAL,
        pct_vap_nh_apamind_aknative REAL,
        pct_vap_nh_asian REAL,
        pct_vap_nh_apasian REAL,
        pct_vap_nh_hawaii_pi REAL,
        pct_vap_nh_aphawaii_pi REAL,
        pct_vap_nh_other_single_race REAL,
        pct_vap_nh_multiracial REAL,
        pct_pop_group_quarters_total REAL,
        pct_pop_correctional REAL,
        pct_pop_juvenile REAL,
        pct_pop_nursing REAL,
        pct_pop_other_inst REAL,
        pct_pop_university REAL,
        pct_pop_military REAL,
        pct_pop_other_noninst REAL
    );
    SELECT gpkgAddGeometryColumn("block{dec_yy}", "geom", "MULTIPOLYGON", 0, 0, 4269);
    SELECT gpkgAddGeometryTriggers("block{dec_yy}", "geom");
    SELECT gpkgAddSpatialIndex("block{dec_yy}", "geom");
    CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_vtd ON block{dec_yy} (statefp, countyfp, vtd);
    CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_countyid ON block{dec_yy} (countyid);
    CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_vtdid ON block{dec_yy} (vtdid);
    CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_placeid ON block{dec_yy} (placeid);
    CREATE INDEX IF NOT EXISTS idx_block{dec_yy}_cousubid ON block{dec_yy} (cousubid);
    """

# Place
create_place_sql = """
    CREATE TABLE IF NOT EXISTS place{dec_yy} (
        fid integer NOT NULL PRIMARY KEY,
        geoid TEXT(15) NOT NULL UNIQUE,
        name TEXT NOT NULL,
        statefp TEXT(5) NOT NULL,
        placefp TEXT(10) NOT NULL,
        classfp TEXT(5),
        pop_total INTEGER, --p0010001
        pop_white INTEGER, --p0010003
        pop_black INTEGER, --p0010004
        pop_apblack INTEGER, --p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071
        pop_amind_aknative INTEGER, --p0010005
        pop_apamind_aknative INTEGER, --p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071
        pop_asian INTEGER, --p0010006
        pop_apasian INTEGER, --p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071
        pop_hawaii_pi INTEGER, --p0010007
        pop_aphawaii_pi INTEGER, --p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071
        pop_other_single_race INTEGER, --p0010008
        pop_multiracial INTEGER, --p0010009
        pop_hispanic INTEGER, --p0020002
        pop_nh_white INTEGER, --p0020005
        pop_nh_black INTEGER, --p0020006
        pop_nh_apblack INTEGER, --p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073
        pop_nh_amind_aknative INTEGER, --p0020007
        pop_nh_apamind_aknative INTEGER, --p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073
        pop_nh_asian INTEGER, --p0020008
        pop_nh_apasian INTEGER, --p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073
        pop_hn_hawaii_pi INTEGER, --p0020009
        pop_nh_aphawaii_pi INTEGER, --p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073
        pop_nh_other_single_race INTEGER, --p0020010
        pop_nh_multiracial INTEGER, --p0020011
        vap_total INTEGER, --p0030001
        vap_white INTEGER, --p0030003
        vap_black INTEGER, --p0030004
        vap_apblack INTEGER, --p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071
        vap_multiracial_black INTEGER, --p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071
        vap_black_black_white INTEGER, --p0030004 + P0030011
        vap_amind_aknative INTEGER, --p0030005
        vap_apamind_aknative INTEGER, --p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071
        vap_asian INTEGER, --p0030006
        vap_apasian INTEGER, --p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071
        vap_hawaii_pi INTEGER, --p0030007
        vap_aphawaii_pi INTEGER, --p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071
        vap_other_single_race INTEGER, --p0030008
        vap_multiracial INTEGER, --p0030009
        vap_hispanic INTEGER, --p0040002
        vap_nh_white INTEGER, --p0040005
        vap_nh_black INTEGER, --p0040006
        vap_nh_apblack INTEGER, --p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073
        vap_nh_dojblack INTEGER, --p0040006 + p0040013
        vap_nh_multiracial_black INTEGER, --p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073
        vap_nh_amind_aknative INTEGER, --p0040007
        vap_nh_apamind_aknative INTEGER, --p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073
        vap_nh_asian INTEGER, --p0040008
        vap_nh_apasian INTEGER, --p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073
        vap_nh_hawaii_pi INTEGER, --p0040009
        vap_nh_aphawaii_pi INTEGER, --p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073
        vap_nh_other_single_race INTEGER, --p0040010
        vap_nh_multiracial INTEGER, --p0040011
        pop_group_quarters_total INTEGER, --p0050001
        pop_correctional INTEGER, --p0050003
        pop_juvenile INTEGER, --p0050004
        pop_nursing INTEGER, --p0050005
        pop_other_inst INTEGER, --p0050006
        pop_university INTEGER, --p0050008
        pop_military INTEGER, --p0050009
        pop_other_noninst INTEGER, --p0050010
        pct_pop_white REAL,
        pct_pop_black REAL,
        pct_pop_apblack REAL,
        pct_pop_amind_aknative REAL,
        pct_pop_apamind_aknative REAL,
        pct_pop_asian REAL,
        pct_pop_apasian REAL,
        pct_pop_hawaii_pi REAL,
        pct_pop_aphawaii_pi REAL,
        pct_pop_other_single_race REAL,
        pct_pop_multiracial REAL,
        pct_pop_hispanic REAL,
        pct_pop_nh_white REAL,
        pct_pop_nh_black REAL,
        pct_pop_nh_apblack REAL,
        pct_pop_nh_amind_aknative REAL,
        pct_pop_nh_apamind_aknative REAL,
        pct_pop_nh_asian REAL,
        pct_pop_nh_apasian REAL,
        pct_pop_hn_hawaii_pi REAL,
        pct_pop_hn_aphawaii_pi REAL,
        pct_pop_nh_other_single_race REAL,
        pct_pop_nh_multiracial REAL,
        pct_vap_white REAL,
        pct_vap_black REAL,
        pct_vap_apblack REAL,
        pct_vap_amind_aknative REAL,
        pct_vap_apamind_aknative REAL,
        pct_vap_asian REAL,
        pct_vap_apasian REAL,
        pct_vap_hawaii_pi REAL,
        pct_vap_aphawaii_pi REAL,
        pct_vap_other_single_race REAL,
        pct_vap_multiracial REAL,
        pct_vap_hispanic REAL,
        pct_vap_nh_white REAL,
        pct_vap_nh_black REAL,
        pct_vap_nh_apblack REAL,
        pct_vap_nh_amind_aknative REAL,
        pct_vap_nh_apamind_aknative REAL,
        pct_vap_nh_asian REAL,
        pct_vap_nh_apasian REAL,
        pct_vap_nh_hawaii_pi REAL,
        pct_vap_nh_aphawaii_pi REAL,
        pct_vap_nh_other_single_race REAL,
        pct_vap_nh_multiracial REAL,
        pct_pop_group_quarters_total REAL,
        pct_pop_correctional REAL,
        pct_pop_juvenile REAL,
        pct_pop_nursing REAL,
        pct_pop_other_inst REAL,
        pct_pop_university REAL,
        pct_pop_military REAL,
        pct_pop_other_noninst REAL
    );
    SELECT gpkgAddGeometryColumn("place{dec_yy}", "geom", "MULTIPOLYGON", 0, 0, (SELECT srs_id FROM gpkg_geometry_columns WHERE table_name = 'pl2020_place'));
    SELECT gpkgAddGeometryTriggers("place{dec_yy}", "geom");
    SELECT gpkgAddSpatialIndex("place{dec_yy}", "geom");
    """

# Inserts
insert_county_data = """
    INSERT INTO county{dec_yy} (
        fid,
        geoid,
        statefp,
        countyfp,
        name,
        pop_total,
        pop_white,
        pop_black,
        pop_apblack,
        pop_amind_aknative,
        pop_apamind_aknative,
        pop_asian,
        pop_apasian,
        pop_hawaii_pi,
        pop_aphawaii_pi,
        pop_other_single_race,
        pop_multiracial,
        pop_hispanic,
        pop_nh_white,
        pop_nh_black,
        pop_nh_apblack,
        pop_nh_amind_aknative,
        pop_nh_apamind_aknative,
        pop_nh_asian,
        pop_nh_apasian,
        pop_hn_hawaii_pi,
        pop_nh_aphawaii_pi,
        pop_nh_other_single_race,
        pop_nh_multiracial,
        vap_total,
        vap_white,
        vap_black,
        vap_apblack,
        vap_multiracial_black,
        vap_black_black_white,
        vap_amind_aknative,
        vap_apamind_aknative,
        vap_asian,
        vap_apasian,
        vap_hawaii_pi,
        vap_aphawaii_pi,
        vap_other_single_race,
        vap_multiracial,
        vap_hispanic,
        vap_nh_white,
        vap_nh_black,
        vap_nh_apblack,
        vap_nh_dojblack,
        vap_nh_multiracial_black,
        vap_nh_amind_aknative,
        vap_nh_apamind_aknative,
        vap_nh_asian,
        vap_nh_apasian,
        vap_nh_hawaii_pi,
        vap_nh_aphawaii_pi,
        vap_nh_other_single_race,
        vap_nh_multiracial,
        pop_group_quarters_total,
        pop_correctional,
        pop_juvenile,
        pop_nursing,
        pop_other_inst,
        pop_university,
        pop_military,
        pop_other_noninst,
        pct_pop_white,
        pct_pop_black,
        pct_pop_apblack,
        pct_pop_amind_aknative,
        pct_pop_apamind_aknative,
        pct_pop_asian,
        pct_pop_apasian,
        pct_pop_hawaii_pi,
        pct_pop_aphawaii_pi,
        pct_pop_other_single_race,
        pct_pop_multiracial,
        pct_pop_hispanic,
        pct_pop_nh_white,
        pct_pop_nh_black,
        pct_pop_nh_apblack,
        pct_pop_nh_amind_aknative,
        pct_pop_nh_apamind_aknative,
        pct_pop_nh_asian,
        pct_pop_nh_apasian,
        pct_pop_hn_hawaii_pi,
        pct_pop_hn_aphawaii_pi,
        pct_pop_nh_other_single_race,
        pct_pop_nh_multiracial,
        pct_vap_white,
        pct_vap_black,
        pct_vap_apblack,
        pct_vap_amind_aknative,
        pct_vap_apamind_aknative,
        pct_vap_asian,
        pct_vap_apasian,
        pct_vap_hawaii_pi,
        pct_vap_aphawaii_pi,
        pct_vap_other_single_race,
        pct_vap_multiracial,
        pct_vap_hispanic,
        pct_vap_nh_white,
        pct_vap_nh_black,
        pct_vap_nh_apblack,
        pct_vap_nh_amind_aknative,
        pct_vap_nh_apamind_aknative,
        pct_vap_nh_asian,
        pct_vap_nh_apasian,
        pct_vap_nh_hawaii_pi,
        pct_vap_nh_aphawaii_pi,
        pct_vap_nh_other_single_race,
        pct_vap_nh_multiracial,
        pct_pop_group_quarters_total,
        pct_pop_correctional,
        pct_pop_juvenile,
        pct_pop_nursing,
        pct_pop_other_inst,
        pct_pop_university,
        pct_pop_military,
        pct_pop_other_noninst,
        geom
    )
    SELECT pl.fid,
        pl.geoid{dec_yy},
        pl.statefp{dec_yy},
        pl.countyfp{dec_yy},
        pl.name{dec_yy},
        p0010001 AS pop_total,
        p0010003 AS pop_white,
        p0010004 AS pop_black,
        p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071 AS pop_apblack,
        p0010005 AS pop_amind_aknative,
        p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071 AS pop_apamind_aknative,
        p0010006 AS pop_asian,
        p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071 AS pop_apasian,
        p0010007 AS pop_hawaii_pi,
        p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071 AS pop_aphawaii_pi,
        p0010008 AS pop_other_single_race,
        p0010009 AS pop_multiracial,
        p0020002 AS pop_hispanic,
        p0020005 AS pop_nh_white,
        p0020006 AS pop_nh_black,
        p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073 AS pop_nh_apblack,
        p0020007 AS pop_nh_amind_aknative,
        p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073 AS pop_nh_apamind_aknative,
        p0020008 AS pop_nh_asian,
        p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073 AS pop_nh_apasian,
        p0020009 AS pop_hn_hawaii_pi,
        p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073 AS pop_nh_aphawaii_pi,
        p0020010 AS pop_nh_other_single_race,
        p0020011 AS pop_nh_multiracial,
        p0030001 AS vap_total,
        p0030003 AS vap_white,
        p0030004 AS vap_black,
        p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071 AS vap_apblack,
        p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071 AS vap_multiracial_black,
        p0030004 + P0030011 AS vap_black_black_white,
        p0030005 AS vap_amind_aknative,
        p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071 AS vap_apamind_aknative,
        p0030006 AS vap_asian,
        p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071 AS vap_apasian,
        p0030007 AS vap_hawaii_pi,
        p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071 AS vap_aphawaii_pi,
        p0030008 AS vap_other_single_race,
        p0030009 AS vap_multiracial,
        p0040002 AS vap_hispanic,
        p0040005 AS vap_nh_white,
        p0040006 AS vap_nh_black,
        p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073 AS vap_nh_apblack,
        p0040006 + p0040013 as vap_nh_dojblack,
        p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073 AS vap_nh_multiracial_black,
        p0040007 AS vap_nh_amind_aknative,
        p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073 AS vap_nh_apamind_aknative,
        p0040008 AS vap_nh_asian,
        p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073 AS vap_nh_apasian,
        p0040009 AS vap_nh_hawaii_pi,
        p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073 AS vap_nh_aphawaii_pi,
        p0040010 AS vap_nh_other_single_race,
        p0040011 AS vap_nh_multiracial,
        p0050001 AS pop_group_quarters_total,
        p0050003 AS pop_correctional,
        p0050004 AS pop_juvenile,
        p0050005 AS pop_nursing,
        p0050006 AS pop_other_inst,
        p0050008 AS pop_university,
        p0050009 AS pop_military,
        p0050010 AS pop_other_noninst,
        CAST(p0010003 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_white,
        CAST(p0010004 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_black,
        CAST(
            p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_apblack,
        CAST(p0010005 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_amind_aknative,
        CAST(
            p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_apamind_aknative,
        CAST(p0010006 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_asian,
        CAST(
            p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_apasian,
        CAST(p0010007 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_hawaii_pi,
        CAST(
            p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_aphawaii_pi,
        CAST(p0010008 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_other_single_race,
        CAST(p0010009 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_multiracial,
        CAST(p0020002 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_hispanic,
        CAST(p0020005 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_white,
        CAST(p0020006 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_black,
        CAST(
            p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_nh_apblack,
        CAST(p0020007 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_amind_aknative,
        CAST(
            p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_nh_apamind_aknative,
        CAST(p0020008 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_asian,
        CAST(
            p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_nh_apasian,
        CAST(p0020009 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_hn_hawaii_pi,
        CAST(
            p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_hn_aphawaii_pi,
        CAST(p0020010 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_other_single_race,
        CAST(p0020011 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_multiracial,
        CAST(p0030003 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_white,
        CAST(p0030004 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_black,
        CAST(
            p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_apblack,
        CAST(p0030005 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_amind_aknative,
        CAST(
            p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_apamind_aknative,
        CAST(p0030006 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_asian,
        CAST(
            p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_apasian,
        CAST(p0030007 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_hawaii_pi,
        CAST(
            p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_aphawaii_pi,
        CAST(p0030008 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_other_single_race,
        CAST(p0030009 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_multiracial,
        CAST(p0040002 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_hispanic,
        CAST(p0040005 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_white,
        CAST(p0040006 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_black,
        CAST(
            p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_apblack,
        CAST(p0040007 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_amind_aknative,
        CAST(
            p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_apamind_aknative,
        CAST(p0040008 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_asian,
        CAST(
            p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_apasian,
        CAST(p0040009 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_hawaii_pi,
        CAST(
            p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_aphawaii_pi,
        CAST(p0040010 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_other_single_race,
        CAST(p0040011 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_multiracial,
        CAST(p0050001 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_group_quarters_total,
        CAST(p0050003 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_correctional,
        CAST(p0050004 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_juvenile,
        CAST(p0050005 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nursing,
        CAST(p0050006 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_other_inst,
        CAST(p0050008 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_university,
        CAST(p0050009 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_military,
        CAST(p0050010 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_other_noninst,
        pl.geom
    FROM pl{dec_yyyy}_cnty pl;
"""

insert_vtd_data = """
    INSERT INTO vtd{dec_yy} (
        fid,
        geoid,
        name,
        statefp,
        countyfp,
        vtdst,
        vtdi,
        countyid,
        pop_total,
        pop_white,
        pop_black,
        pop_apblack,
        pop_amind_aknative,
        pop_apamind_aknative,
        pop_asian,
        pop_apasian,
        pop_hawaii_pi,
        pop_aphawaii_pi,
        pop_other_single_race,
        pop_multiracial,
        pop_hispanic,
        pop_nh_white,
        pop_nh_black,
        pop_nh_apblack,
        pop_nh_amind_aknative,
        pop_nh_apamind_aknative,
        pop_nh_asian,
        pop_nh_apasian,
        pop_hn_hawaii_pi,
        pop_nh_aphawaii_pi,
        pop_nh_other_single_race,
        pop_nh_multiracial,
        vap_total,
        vap_white,
        vap_black,
        vap_apblack,
        vap_multiracial_black,
        vap_black_black_white,
        vap_amind_aknative,
        vap_apamind_aknative,
        vap_asian,
        vap_apasian,
        vap_hawaii_pi,
        vap_aphawaii_pi,
        vap_other_single_race,
        vap_multiracial,
        vap_hispanic,
        vap_nh_white,
        vap_nh_black,
        vap_nh_apblack,
        vap_nh_dojblack,
        vap_nh_multiracial_black,
        vap_nh_amind_aknative,
        vap_nh_apamind_aknative,
        vap_nh_asian,
        vap_nh_apasian,
        vap_nh_hawaii_pi,
        vap_nh_aphawaii_pi,
        vap_nh_other_single_race,
        vap_nh_multiracial,
        pop_group_quarters_total,
        pop_correctional,
        pop_juvenile,
        pop_nursing,
        pop_other_inst,
        pop_university,
        pop_military,
        pop_other_noninst,
        pct_pop_white,
        pct_pop_black,
        pct_pop_apblack,
        pct_pop_amind_aknative,
        pct_pop_apamind_aknative,
        pct_pop_asian,
        pct_pop_apasian,
        pct_pop_hawaii_pi,
        pct_pop_aphawaii_pi,
        pct_pop_other_single_race,
        pct_pop_multiracial,
        pct_pop_hispanic,
        pct_pop_nh_white,
        pct_pop_nh_black,
        pct_pop_nh_apblack,
        pct_pop_nh_amind_aknative,
        pct_pop_nh_apamind_aknative,
        pct_pop_nh_asian,
        pct_pop_nh_apasian,
        pct_pop_hn_hawaii_pi,
        pct_pop_hn_aphawaii_pi,
        pct_pop_nh_other_single_race,
        pct_pop_nh_multiracial,
        pct_vap_white,
        pct_vap_black,
        pct_vap_apblack,
        pct_vap_amind_aknative,
        pct_vap_apamind_aknative,
        pct_vap_asian,
        pct_vap_apasian,
        pct_vap_hawaii_pi,
        pct_vap_aphawaii_pi,
        pct_vap_other_single_race,
        pct_vap_multiracial,
        pct_vap_hispanic,
        pct_vap_nh_white,
        pct_vap_nh_black,
        pct_vap_nh_apblack,
        pct_vap_nh_amind_aknative,
        pct_vap_nh_apamind_aknative,
        pct_vap_nh_asian,
        pct_vap_nh_apasian,
        pct_vap_nh_hawaii_pi,
        pct_vap_nh_aphawaii_pi,
        pct_vap_nh_other_single_race,
        pct_vap_nh_multiracial,
        pct_pop_group_quarters_total,
        pct_pop_correctional,
        pct_pop_juvenile,
        pct_pop_nursing,
        pct_pop_other_inst,
        pct_pop_university,
        pct_pop_military,
        pct_pop_other_noninst,
        geom
    )
    SELECT pl.fid,
        pl.geoid{dec_yy},
        pl.name{dec_yy},
        pl.statefp{dec_yy},
        pl.countyfp{dec_yy},
        pl.vtdst{dec_yy},
        pl.vtdi{dec_yy},
        pl.statefp{dec_yy} || pl.countyfp{dec_yy} as countyid,
        p0010001 AS pop_total,
        p0010003 AS pop_white,
        p0010004 AS pop_black,
        p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071 AS pop_apblack,
        p0010005 AS pop_amind_aknative,
        p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071 AS pop_apamind_aknative,
        p0010006 AS pop_asian,
        p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071 AS pop_apasian,
        p0010007 AS pop_hawaii_pi,
        p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071 AS pop_aphawaii_pi,
        p0010008 AS pop_other_single_race,
        p0010009 AS pop_multiracial,
        p0020002 AS pop_hispanic,
        p0020005 AS pop_nh_white,
        p0020006 AS pop_nh_black,
        p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073 AS pop_nh_apblack,
        p0020007 AS pop_nh_amind_aknative,
        p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073 AS pop_nh_apamind_aknative,
        p0020008 AS pop_nh_asian,
        p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073 AS pop_nh_apasian,
        p0020009 AS pop_hn_hawaii_pi,
        p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073 AS pop_nh_aphawaii_pi,
        p0020010 AS pop_nh_other_single_race,
        p0020011 AS pop_nh_multiracial,
        p0030001 AS vap_total,
        p0030003 AS vap_white,
        p0030004 AS vap_black,
        p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071 AS vap_apblack,
        p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071 AS vap_multiracial_black,
        p0030004 + P0030011 AS vap_black_black_white,
        p0030005 AS vap_amind_aknative,
        p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071 AS vap_apamind_aknative,
        p0030006 AS vap_asian,
        p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071 AS vap_apasian,
        p0030007 AS vap_hawaii_pi,
        p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071 AS vap_aphawaii_pi,
        p0030008 AS vap_other_single_race,
        p0030009 AS vap_multiracial,
        p0040002 AS vap_hispanic,
        p0040005 AS vap_nh_white,
        p0040006 AS vap_nh_black,
        p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073 AS vap_nh_apblack,
        p0040006 + p0040013 as vap_nh_dojblack,
        p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073 AS vap_nh_multiracial_black,
        p0040007 AS vap_nh_amind_aknative,
        p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073 AS vap_nh_apamind_aknative,
        p0040008 AS vap_nh_asian,
        p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073 AS vap_nh_apasian,
        p0040009 AS vap_nh_hawaii_pi,
        p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073 AS vap_nh_aphawaii_pi,
        p0040010 AS vap_nh_other_single_race,
        p0040011 AS vap_nh_multiracial,
        p0050001 AS pop_group_quarters_total,
        p0050003 AS pop_correctional,
        p0050004 AS pop_juvenile,
        p0050005 AS pop_nursing,
        p0050006 AS pop_other_inst,
        p0050008 AS pop_university,
        p0050009 AS pop_military,
        p0050010 AS pop_other_noninst,
        CAST(p0010003 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_white,
        CAST(p0010004 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_black,
        CAST(
            p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_apblack,
        CAST(p0010005 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_amind_aknative,
        CAST(
            p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_apamind_aknative,
        CAST(p0010006 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_asian,
        CAST(
            p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_apasian,
        CAST(p0010007 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_hawaii_pi,
        CAST(
            p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_aphawaii_pi,
        CAST(p0010008 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_other_single_race,
        CAST(p0010009 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_multiracial,
        CAST(p0020002 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_hispanic,
        CAST(p0020005 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_white,
        CAST(p0020006 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_black,
        CAST(
            p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_nh_apblack,
        CAST(p0020007 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_amind_aknative,
        CAST(
            p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_nh_apamind_aknative,
        CAST(p0020008 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_asian,
        CAST(
            p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_nh_apasian,
        CAST(p0020009 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_hn_hawaii_pi,
        CAST(
            p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_hn_aphawaii_pi,
        CAST(p0020010 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_other_single_race,
        CAST(p0020011 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_multiracial,
        CAST(p0030003 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_white,
        CAST(p0030004 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_black,
        CAST(
            p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_apblack,
        CAST(p0030005 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_amind_aknative,
        CAST(
            p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_apamind_aknative,
        CAST(p0030006 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_asian,
        CAST(
            p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_apasian,
        CAST(p0030007 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_hawaii_pi,
        CAST(
            p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_aphawaii_pi,
        CAST(p0030008 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_other_single_race,
        CAST(p0030009 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_multiracial,
        CAST(p0040002 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_hispanic,
        CAST(p0040005 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_white,
        CAST(p0040006 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_black,
        CAST(
            p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_apblack,
        CAST(p0040007 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_amind_aknative,
        CAST(
            p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_apamind_aknative,
        CAST(p0040008 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_asian,
        CAST(
            p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_apasian,
        CAST(p0040009 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_hawaii_pi,
        CAST(
            p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_aphawaii_pi,
        CAST(p0040010 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_other_single_race,
        CAST(p0040011 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_multiracial,
        CAST(p0050001 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_group_quarters_total,
        CAST(p0050003 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_correctional,
        CAST(p0050004 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_juvenile,
        CAST(p0050005 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nursing,
        CAST(p0050006 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_other_inst,
        CAST(p0050008 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_university,
        CAST(p0050009 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_military,
        CAST(p0050010 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_other_noninst,
        pl.geom
    FROM pl{dec_yyyy}_vtd pl;
"""

insert_block_data = """
    INSERT INTO block{dec_yy}
    SELECT pl.fid,
        pl.geoid{dec_yy},
        pl.statefp{dec_yy},
        pl.countyfp{dec_yy},
        pl.tractce{dec_yy},
        pl.blockce{dec_yy},
        pl.blkgrp,
        pl.vtd,
        pl.cousub,
        pl.place,
        pl.statefp{dec_yy} || pl.countyfp{dec_yy} as countyid,
        pl.statefp{dec_yy} || pl.countyfp{dec_yy} || pl.tractce20 as tractid,
        pl.statefp{dec_yy} || pl.countyfp{dec_yy} || pl.tractce20 || blkgrp as blkgrpid,
        pl.statefp{dec_yy} || pl.countyfp{dec_yy} || vtd as vtdid,
        pl.statefp{dec_yy} || pl.place as placeid,
        pl.statefp{dec_yy} || pl.countyfp{dec_yy} || pl.cousub as cousubid,
        p0010001 AS pop_total,
        p0010003 AS pop_white,
        p0010004 AS pop_black,
        p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071 AS pop_apblack,
        p0010005 AS pop_amind_aknative,
        p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071 AS pop_apamind_aknative,
        p0010006 AS pop_asian,
        p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071 AS pop_apasian,
        p0010007 AS pop_hawaii_pi,
        p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071 AS pop_aphawaii_pi,
        p0010008 AS pop_other_single_race,
        p0010009 AS pop_multiracial,
        p0020002 AS pop_hispanic,
        p0020005 AS pop_nh_white,
        p0020006 AS pop_nh_black,
        p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073 AS pop_nh_apblack,
        p0020007 AS pop_nh_amind_aknative,
        p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073 AS pop_nh_apamind_aknative,
        p0020008 AS pop_nh_asian,
        p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073 AS pop_nh_apasian,
        p0020009 AS pop_hn_hawaii_pi,
        p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073 AS pop_nh_aphawaii_pi,
        p0020010 AS pop_nh_other_single_race,
        p0020011 AS pop_nh_multiracial,
        p0030001 AS vap_total,
        p0030003 AS vap_white,
        p0030004 AS vap_black,
        p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071 AS vap_apblack,
        p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071 AS vap_multiracial_black,
        p0030004 + P0030011 AS vap_black_black_white,
        p0030005 AS vap_amind_aknative,
        p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071 AS vap_apamind_aknative,
        p0030006 AS vap_asian,
        p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071 AS vap_apasian,
        p0030007 AS vap_hawaii_pi,
        p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071 AS vap_aphawaii_pi,
        p0030008 AS vap_other_single_race,
        p0030009 AS vap_multiracial,
        p0040002 AS vap_hispanic,
        p0040005 AS vap_nh_white,
        p0040006 AS vap_nh_black,
        p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073 AS vap_nh_apblack,
        p0040006 + p0040013 as vap_nh_dojblack,
        p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073 AS vap_nh_multiracial_black,
        p0040007 AS vap_nh_amind_aknative,
        p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073 AS vap_nh_apamind_aknative,
        p0040008 AS vap_nh_asian,
        p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073 AS vap_nh_apasian,
        p0040009 AS vap_nh_hawaii_pi,
        p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073 AS vap_nh_aphawaii_pi,
        p0040010 AS vap_nh_other_single_race,
        p0040011 AS vap_nh_multiracial,
        p0050001 AS pop_group_quarters_total,
        p0050003 AS pop_correctional,
        p0050004 AS pop_juvenile,
        p0050005 AS pop_nursing,
        p0050006 AS pop_other_inst,
        p0050008 AS pop_university,
        p0050009 AS pop_military,
        p0050010 AS pop_other_noninst,
        CAST(p0010003 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_white,
        CAST(p0010004 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_black,
        CAST(
            p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_apblack,
        CAST(p0010005 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_amind_aknative,
        CAST(
            p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_apamind_aknative,
        CAST(p0010006 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_asian,
        CAST(
            p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_apasian,
        CAST(p0010007 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_hawaii_pi,
        CAST(
            p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_aphawaii_pi,
        CAST(p0010008 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_other_single_race,
        CAST(p0010009 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_multiracial,
        CAST(p0020002 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_hispanic,
        CAST(p0020005 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_white,
        CAST(p0020006 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_black,
        CAST(
            p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_nh_apblack,
        CAST(p0020007 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_amind_aknative,
        CAST(
            p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_nh_apamind_aknative,
        CAST(p0020008 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_asian,
        CAST(
            p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_nh_apasian,
        CAST(p0020009 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_hn_hawaii_pi,
        CAST(
            p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_hn_aphawaii_pi,
        CAST(p0020010 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_other_single_race,
        CAST(p0020011 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nh_multiracial,
        CAST(p0030003 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_white,
        CAST(p0030004 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_black,
        CAST(
            p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_apblack,
        CAST(p0030005 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_amind_aknative,
        CAST(
            p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_apamind_aknative,
        CAST(p0030006 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_asian,
        CAST(
            p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_apasian,
        CAST(p0030007 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_hawaii_pi,
        CAST(
            p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_aphawaii_pi,
        CAST(p0030008 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_other_single_race,
        CAST(p0030009 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_multiracial,
        CAST(p0040002 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_hispanic,
        CAST(p0040005 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_white,
        CAST(p0040006 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_black,
        CAST(
            p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_apblack,
        CAST(p0040007 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_amind_aknative,
        CAST(
            p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_apamind_aknative,
        CAST(p0040008 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_asian,
        CAST(
            p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_apasian,
        CAST(p0040009 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_hawaii_pi,
        CAST(
            p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_aphawaii_pi,
        CAST(p0040010 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_other_single_race,
        CAST(p0040011 AS REAL) / NULLIF(p0030001, 0) AS pct_vap_nh_multiracial,
        CAST(p0050001 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_group_quarters_total,
        CAST(p0050003 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_correctional,
        CAST(p0050004 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_juvenile,
        CAST(p0050005 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_nursing,
        CAST(p0050006 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_other_inst,
        CAST(p0050008 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_university,
        CAST(p0050009 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_military,
        CAST(p0050010 AS REAL) / NULLIF(p0010001, 0) AS pct_pop_other_noninst,
        pl.geom
    FROM pl{dec_yyyy}_b pl;
    """

insert_place_data = """
    CREATE INDEX IF NOT EXISTS idx_place{dec_yy}_place ON place{dec_yy} (statefp, placefp);
    INSERT INTO place{dec_yy} (
        fid,
        geoid,
        name,
        statefp,
        placefp,
        classfp,
        pop_total,
        pop_white,
        pop_black,
        pop_apblack,
        pop_amind_aknative,
        pop_apamind_aknative,
        pop_asian,
        pop_apasian,
        pop_hawaii_pi,
        pop_aphawaii_pi,
        pop_other_single_race,
        pop_multiracial,
        pop_hispanic,
        pop_nh_white,
        pop_nh_black,
        pop_nh_apblack,
        pop_nh_amind_aknative,
        pop_nh_apamind_aknative,
        pop_nh_asian,
        pop_nh_apasian,
        pop_hn_hawaii_pi,
        pop_nh_aphawaii_pi,
        pop_nh_other_single_race,
        pop_nh_multiracial,
        vap_total,
        vap_white,
        vap_black,
        vap_apblack,
        vap_multiracial_black,
        vap_black_black_white,
        vap_amind_aknative,
        vap_apamind_aknative,
        vap_asian,
        vap_apasian,
        vap_hawaii_pi,
        vap_aphawaii_pi,
        vap_other_single_race,
        vap_multiracial,
        vap_hispanic,
        vap_nh_white,
        vap_nh_black,
        vap_nh_apblack,
        vap_nh_dojblack,
        vap_nh_multiracial_black,
        vap_nh_amind_aknative,
        vap_nh_apamind_aknative,
        vap_nh_asian,
        vap_nh_apasian,
        vap_nh_hawaii_pi,
        vap_nh_aphawaii_pi,
        vap_nh_other_single_race,
        vap_nh_multiracial,
        pop_group_quarters_total,
        pop_correctional,
        pop_juvenile,
        pop_nursing,
        pop_other_inst,
        pop_university,
        pop_military,
        pop_other_noninst,
        pct_pop_white,
        pct_pop_black,
        pct_pop_apblack,
        pct_pop_amind_aknative,
        pct_pop_apamind_aknative,
        pct_pop_asian,
        pct_pop_apasian,
        pct_pop_hawaii_pi,
        pct_pop_aphawaii_pi,
        pct_pop_other_single_race,
        pct_pop_multiracial,
        pct_pop_hispanic,
        pct_pop_nh_white,
        pct_pop_nh_black,
        pct_pop_nh_apblack,
        pct_pop_nh_amind_aknative,
        pct_pop_nh_apamind_aknative,
        pct_pop_nh_asian,
        pct_pop_nh_apasian,
        pct_pop_hn_hawaii_pi,
        pct_pop_hn_aphawaii_pi,
        pct_pop_nh_other_single_race,
        pct_pop_nh_multiracial,
        pct_vap_white,
        pct_vap_black,
        pct_vap_apblack,
        pct_vap_amind_aknative,
        pct_vap_apamind_aknative,
        pct_vap_asian,
        pct_vap_apasian,
        pct_vap_hawaii_pi,
        pct_vap_aphawaii_pi,
        pct_vap_other_single_race,
        pct_vap_multiracial,
        pct_vap_hispanic,
        pct_vap_nh_white,
        pct_vap_nh_black,
        pct_vap_nh_apblack,
        pct_vap_nh_amind_aknative,
        pct_vap_nh_apamind_aknative,
        pct_vap_nh_asian,
        pct_vap_nh_apasian,
        pct_vap_nh_hawaii_pi,
        pct_vap_nh_aphawaii_pi,
        pct_vap_nh_other_single_race,
        pct_vap_nh_multiracial,
        pct_pop_group_quarters_total,
        pct_pop_correctional,
        pct_pop_juvenile,
        pct_pop_nursing,
        pct_pop_other_inst,
        pct_pop_university,
        pct_pop_military,
        pct_pop_other_noninst,
        geom
    )
    SELECT pl.fid,
        pl.geoid{dec_yy},
        pl.name{dec_yy},
        pl.statefp{dec_yy},
        pl.placefp{dec_yy},
        pl.classfp{dec_yy},
        p0010001 AS pop_total,
        p0010003 AS pop_white,
        p0010004 AS pop_black,
        p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071 AS pop_apblack,
        p0010005 AS pop_amind_aknative,
        p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071 AS pop_apamind_aknative,
        p0010006 AS pop_asian,
        p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071 AS pop_apasian,
        p0010007 AS pop_hawaii_pi,
        p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071 AS pop_aphawaii_pi,
        p0010008 AS pop_other_single_race,
        p0010009 AS pop_multiracial,
        p0020002 AS pop_hispanic,
        p0020005 AS pop_nh_white,
        p0020006 AS pop_nh_black,
        p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073 AS pop_nh_apblack,
        p0020007 AS pop_nh_amind_aknative,
        p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073 AS pop_nh_apamind_aknative,
        p0020008 AS pop_nh_asian,
        p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073 AS pop_nh_apasian,
        p0020009 AS pop_hn_hawaii_pi,
        p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073 AS pop_nh_aphawaii_pi,
        p0020010 AS pop_nh_other_single_race,
        p0020011 AS pop_nh_multiracial,
        p0030001 AS vap_total,
        p0030003 AS vap_white,
        p0030004 AS vap_black,
        p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071 AS vap_apblack,
        p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071 AS vap_multiracial_black,
        p0030004 + P0030011 AS vap_black_black_white,
        p0030005 AS vap_amind_aknative,
        p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071 AS vap_apamind_aknative,
        p0030006 AS vap_asian,
        p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071 AS vap_apasian,
        p0030007 AS vap_hawaii_pi,
        p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071 AS vap_aphawaii_pi,
        p0030008 AS vap_other_single_race,
        p0030009 AS vap_multiracial,
        p0040002 AS vap_hispanic,
        p0040005 AS vap_nh_white,
        p0040006 AS vap_nh_black,
        p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073 AS vap_nh_apblack,
        p0040006 + p0040013 as vap_nh_dojblack,
        p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073 AS vap_nh_multiracial_black,
        p0040007 AS vap_nh_amind_aknative,
        p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073 AS vap_nh_apamind_aknative,
        p0040008 AS vap_nh_asian,
        p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073 AS vap_nh_apasian,
        p0040009 AS vap_nh_hawaii_pi,
        p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073 AS vap_nh_aphawaii_pi,
        p0040010 AS vap_nh_other_single_race,
        p0040011 AS vap_nh_multiracial,
        p0050001 AS pop_group_quarters_total,
        p0050003 AS pop_correctional,
        p0050004 AS pop_juvenile,
        p0050005 AS pop_nursing,
        p0050006 AS pop_other_inst,
        p0050008 AS pop_university,
        p0050009 AS pop_military,
        p0050010 AS pop_other_noninst,
        CAST(p0010003 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_white,
        CAST(p0010004 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_black,
        CAST(
            p0010004 + p0010011 + p0010016 + p0010017 + p0010018 + p0010019 + p0010027 + p0010028 + p0010029 + p0010030 + p0010037 + p0010038 + p0010039 + p0010040 + p0010041 + p0010042 + p0010048 + p0010049 + p0010050 + p0010051 + p0010052 + p0010053 + p0010058 + p0010059 + p0010060 + p0010061 + p0010064 + p0010065 + p0010066 + p0010067 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_apblack,
        CAST(p0010005 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_amind_aknative,
        CAST(
            p0010005 + p0010012 + p0010016 + p0010020 + p0010021 + p0010022 + p0010027 + p0010031 + p0010032 + p0010033 + p0010037 + p0010038 + p0010039 + p0010043 + p0010044 + p0010045 + p0010048 + p0010049 + p0010050 + p0010054 + p0010055 + p0010056 + p0010058 + p0010059 + p0010060 + p0010062 + p0010064 + p0010065 + p0010066 + p0010068 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_apamind_aknative,
        CAST(p0010006 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_asian,
        CAST(
            p0010006 + p0010013 + p0010017 + p0010020 + p0010023 + p0010024 + p0010028 + p0010031 + p0010034 + p0010035 + p0010037 + p0010040 + p0010041 + p0010043 + p0010044 + p0010046 + p0010048 + p0010051 + p0010052 + p0010054 + p0010055 + p0010057 + p0010058 + p0010059 + p0010061 + p0010062 + p0010064 + p0010065 + p0010067 + p0010068 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_apasian,
        CAST(p0010007 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_hawaii_pi,
        CAST(
            p0010007 + p0010014 + p0010018 + p0010021 + p0010023 + p0010025 + p0010029 + p0010032 + p0010034 + p0010036 + p0010038 + p0010040 + p0010042 + p0010043 + p0010045 + p0010046 + p0010049 + p0010051 + p0010053 + p0010054 + p0010056 + p0010057 + p0010058 + p0010060 + p0010061 + p0010062 + p0010064 + p0010066 + p0010067 + p0010068 + p0010069 + p0010071 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_aphawaii_pi,
        CAST(p0010008 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_other_single_race,
        CAST(p0010009 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_multiracial,
        CAST(p0020002 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_hispanic,
        CAST(p0020005 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_nh_white,
        CAST(p0020006 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_nh_black,
        CAST(
            p0020006 + p0020013 + p0020018 + p0020019 + p0020020 + p0020021 + p0020029 + p0020030 + p0020031 + p0020032 + p0020039 + p0020040 + p0020041 + p0020042 + p0020043 + p0020044 + p0020050 + p0020051 + p0020052 + p0020053 + p0020054 + p0020055 + p0020060 + p0020061 + p0020062 + p0020063 + p0020066 + p0020067 + p0020068 + p0020069 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_nh_apblack,
        CAST(p0020007 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_nh_amind_aknative,
        CAST(
            p0020007 + p0020014 + p0020018 + p0020022 + p0020023 + p0020024 + p0020029 + p0020033 + p0020034 + p0020035 + p0020039 + p0020040 + p0020041 + p0020045 + p0020046 + p0020047 + p0020050 + p0020051 + p0020052 + p0020056 + p0020057 + p0020058 + p0020060 + p0020061 + p0020062 + p0020064 + p0020066 + p0020067 + p0020068 + p0020070 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_nh_apamind_aknative,
        CAST(p0020008 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_nh_asian,
        CAST(
            p0020008 + p0020015 + p0020019 + p0020022 + p0020025 + p0020026 + p0020030 + p0020033 + p0020036 + p0020037 + p0020039 + p0020042 + p0020043 + p0020045 + p0020046 + p0020048 + p0020050 + p0020053 + p0020054 + p0020056 + p0020057 + p0020059 + p0020060 + p0020061 + p0020063 + p0020064 + p0020066 + p0020067 + p0020069 + p0020070 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_nh_apasian,
        CAST(p0020009 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_hn_hawaii_pi,
        CAST(
            p0020009 + p0020016 + p0020020 + p0020023 + p0020025 + p0020027 + p0020031 + p0020034 + p0020036 + p0020038 + p0020040 + p0020042 + p0020044 + p0020045 + p0020047 + p0020048 + p0020051 + p0020053 + p0020055 + p0020056 + p0020058 + p0020059 + p0020060 + p0020062 + p0020063 + p0020064 + p0020066 + p0020068 + p0020069 + p0020070 + p0020071 + p0020073 AS INTEGER
        ) / NULLIF(p0010001, 0) AS pct_pop_hn_aphawaii_pi,
        CAST(p0020010 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_nh_other_single_race,
        CAST(p0020011 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_nh_multiracial,
        CAST(p0030003 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_white,
        CAST(p0030004 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_black,
        CAST(
            p0030004 + p0030011 + p0030016 + p0030017 + p0030018 + p0030019 + p0030027 + p0030028 + p0030029 + p0030030 + p0030037 + p0030038 + p0030039 + p0030040 + p0030041 + p0030042 + p0030048 + p0030049 + p0030050 + p0030051 + p0030052 + p0030053 + p0030058 + p0030059 + p0030060 + p0030061 + p0030064 + p0030065 + p0030066 + p0030067 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_apblack,
        CAST(p0030005 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_amind_aknative,
        CAST(
            p0030005 + p0030012 + p0030016 + p0030020 + p0030021 + p0030022 + p0030027 + p0030031 + p0030032 + p0030033 + p0030037 + p0030038 + p0030039 + p0030043 + p0030044 + p0030045 + p0030048 + p0030049 + p0030050 + p0030054 + p0030055 + p0030056 + p0030058 + p0030059 + p0030060 + p0030062 + p0030064 + p0030065 + p0030066 + p0030068 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_apamind_aknative,
        CAST(p0030006 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_asian,
        CAST(
            p0030006 + p0030013 + p0030017 + p0030020 + p0030023 + p0030024 + p0030028 + p0030031 + p0030034 + p0030035 + p0030037 + p0030040 + p0030041 + p0030043 + p0030044 + p0030046 + p0030048 + p0030051 + p0030052 + p0030054 + p0030055 + p0030057 + p0030058 + p0030059 + p0030061 + p0030062 + p0030064 + p0030065 + p0030067 + p0030068 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_apasian,
        CAST(p0030007 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_hawaii_pi,
        CAST(
            p0030007 + p0030014 + p0030018 + p0030021 + p0030023 + p0030025 + p0030029 + p0030032 + p0030034 + p0030036 + p0030038 + p0030040 + p0030042 + p0030043 + p0030045 + p0030046 + p0030049 + p0030051 + p0030053 + p0030054 + p0030056 + p0030057 + p0030058 + p0030060 + p0030061 + p0030062 + p0030064 + p0030066 + p0030067 + p0030068 + p0030069 + p0030071 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_aphawaii_pi,
        CAST(p0030008 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_other_single_race,
        CAST(p0030009 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_multiracial,
        CAST(p0040002 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_hispanic,
        CAST(p0040005 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_nh_white,
        CAST(p0040006 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_nh_black,
        CAST(
            p0040006 + p0040013 + p0040018 + p0040019 + p0040020 + p0040021 + p0040029 + p0040030 + p0040031 + p0040032 + p0040039 + p0040040 + p0040041 + p0040042 + p0040043 + p0040044 + p0040050 + p0040051 + p0040052 + p0040053 + p0040054 + p0040055 + p0040060 + p0040061 + p0040062 + p0040063 + p0040066 + p0040067 + p0040068 + p0040069 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_apblack,
        CAST(p0040007 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_nh_amind_aknative,
        CAST(
            p0040007 + p0040014 + p0040018 + p0040022 + p0040023 + p0040024 + p0040029 + p0040033 + p0040034 + p0040035 + p0040039 + p0040040 + p0040041 + p0040045 + p0040046 + p0040047 + p0040050 + p0040051 + p0040052 + p0040056 + p0040057 + p0040058 + p0040060 + p0040061 + p0040062 + p0040064 + p0040066 + p0040067 + p0040068 + p0040070 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_apamind_aknative,
        CAST(p0040008 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_nh_asian,
        CAST(
            p0040008 + p0040015 + p0040019 + p0040022 + p0040025 + p0040026 + p0040030 + p0040033 + p0040036 + p0040037 + p0040039 + p0040042 + p0040043 + p0040045 + p0040046 + p0040048 + p0040050 + p0040053 + p0040054 + p0040056 + p0040057 + p0040059 + p0040060 + p0040061 + p0040063 + p0040064 + p0040066 + p0040067 + p0040069 + p0040070 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_apasian,
        CAST(p0040009 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_nh_hawaii_pi,
        CAST(
            p0040009 + p0040016 + p0040020 + p0040023 + p0040025 + p0040027 + p0040031 + p0040034 + p0040036 + p0040038 + p0040040 + p0040042 + p0040044 + p0040045 + p0040047 + p0040048 + p0040051 + p0040053 + p0040055 + p0040056 + p0040058 + p0040059 + p0040060 + p0040062 + p0040063 + p0040064 + p0040066 + p0040068 + p0040069 + p0040070 + p0040071 + p0040073 AS INTEGER
        ) / NULLIF(p0030001, 0) AS pct_vap_nh_aphawaii_pi,
        CAST(p0040010 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_nh_other_single_race,
        CAST(p0040011 AS INTEGER) / NULLIF(p0030001, 0) AS pct_vap_nh_multiracial,
        CAST(p0050001 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_group_quarters_total,
        CAST(p0050003 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_correctional,
        CAST(p0050004 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_juvenile,
        CAST(p0050005 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_nursing,
        CAST(p0050006 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_other_inst,
        CAST(p0050008 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_university,
        CAST(p0050009 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_military,
        CAST(p0050010 AS INTEGER) / NULLIF(p0010001, 0) AS pct_pop_other_noninst,
        pl.geom
    FROM pl{dec_yyyy}_place pl;
    """

add_cvap_fields = """
    ALTER TABLE {table}{dec_yy} ADD COLUMN cvap_{acs_yyyy}_total REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cvap_{acs_yyyy}_nonhispanic REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cvap_{acs_yyyy}_hispanic REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cvap_{acs_yyyy}_amind_aknative REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cvap_{acs_yyyy}_asian REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cvap_{acs_yyyy}_black REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cvap_{acs_yyyy}_hawaii_pi REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cvap_{acs_yyyy}_nh_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cvap_{acs_yyyy}_amind_aknative_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cvap_{acs_yyyy}_asian_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cvap_{acs_yyyy}_black_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cvap_{acs_yyyy}_amind_aknative_black REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cpop_{acs_yyyy}_total REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cpop_{acs_yyyy}_nonhispanic REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cpop_{acs_yyyy}_hispanic REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cpop_{acs_yyyy}_amind_aknative REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cpop_{acs_yyyy}_asian REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cpop_{acs_yyyy}_black REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cpop_{acs_yyyy}_hawaii_pi REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cpop_{acs_yyyy}_nh_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cpop_{acs_yyyy}_amind_aknative_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cpop_{acs_yyyy}_asian_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cpop_{acs_yyyy}_black_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN cpop_{acs_yyyy}_amind_aknative_black REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cvap_{acs_yyyy}_nonhispanic REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cvap_{acs_yyyy}_hispanic REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cvap_{acs_yyyy}_amind_aknative REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cvap_{acs_yyyy}_asian REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cvap_{acs_yyyy}_black REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cvap_{acs_yyyy}_hawaii_pi REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cvap_{acs_yyyy}_nh_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cvap_{acs_yyyy}_amind_aknative_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cvap_{acs_yyyy}_asian_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cvap_{acs_yyyy}_black_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cvap_{acs_yyyy}_amind_aknative_black REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cpop_{acs_yyyy}_nonhispanic REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cpop_{acs_yyyy}_hispanic REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cpop_{acs_yyyy}_amind_aknative REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cpop_{acs_yyyy}_asian REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cpop_{acs_yyyy}_black REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cpop_{acs_yyyy}_hawaii_pi REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cpop_{acs_yyyy}_nh_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cpop_{acs_yyyy}_amind_aknative_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cpop_{acs_yyyy}_asian_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cpop_{acs_yyyy}_black_white REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_cpop_{acs_yyyy}_amind_aknative_black REAL;
    """

insert_cvap_data = """
    CREATE INDEX idx_cvap_{acs_yyyy}_{src_table} ON cvap_{acs_yyyy}_{src_table} ({geoid});
    UPDATE {table}{dec_yy}
        SET (
            cvap_{acs_yyyy}_total,
            cvap_{acs_yyyy}_nonhispanic,
            cvap_{acs_yyyy}_hispanic,
            cvap_{acs_yyyy}_amind_aknative,
            cvap_{acs_yyyy}_asian,
            cvap_{acs_yyyy}_black,
            cvap_{acs_yyyy}_hawaii_pi,
            cvap_{acs_yyyy}_nh_white,
            cvap_{acs_yyyy}_amind_aknative_white,
            cvap_{acs_yyyy}_asian_white,
            cvap_{acs_yyyy}_black_white,
            cvap_{acs_yyyy}_amind_aknative_black,
            cpop_{acs_yyyy}_total,
            cpop_{acs_yyyy}_nonhispanic,
            cpop_{acs_yyyy}_hispanic,
            cpop_{acs_yyyy}_amind_aknative,
            cpop_{acs_yyyy}_asian,
            cpop_{acs_yyyy}_black,
            cpop_{acs_yyyy}_hawaii_pi,
            cpop_{acs_yyyy}_nh_white,
            cpop_{acs_yyyy}_amind_aknative_white,
            cpop_{acs_yyyy}_asian_white,
            cpop_{acs_yyyy}_black_white,
            cpop_{acs_yyyy}_amind_aknative_black,
            pct_cvap_{acs_yyyy}_nonhispanic,
            pct_cvap_{acs_yyyy}_hispanic,
            pct_cvap_{acs_yyyy}_amind_aknative,
            pct_cvap_{acs_yyyy}_asian,
            pct_cvap_{acs_yyyy}_black,
            pct_cvap_{acs_yyyy}_hawaii_pi,
            pct_cvap_{acs_yyyy}_nh_white,
            pct_cvap_{acs_yyyy}_amind_aknative_white,
            pct_cvap_{acs_yyyy}_asian_white,
            pct_cvap_{acs_yyyy}_black_white,
            pct_cvap_{acs_yyyy}_amind_aknative_black,
            pct_cpop_{acs_yyyy}_nonhispanic,
            pct_cpop_{acs_yyyy}_hispanic,
            pct_cpop_{acs_yyyy}_amind_aknative,
            pct_cpop_{acs_yyyy}_asian,
            pct_cpop_{acs_yyyy}_black,
            pct_cpop_{acs_yyyy}_hawaii_pi,
            pct_cpop_{acs_yyyy}_nh_white,
            pct_cpop_{acs_yyyy}_amind_aknative_white,
            pct_cpop_{acs_yyyy}_asian_white,
            pct_cpop_{acs_yyyy}_black_white,
            pct_cpop_{acs_yyyy}_amind_aknative_black
        ) = (
            SELECT CAST(cvap_tot{acs_yy} AS REAL) AS cvap_{acs_yyyy}_total,
                CAST(cvap_nhs{acs_yy} AS REAL) AS cvap_{acs_yyyy}_nonhispanic,
                CAST(cvap_hsp{acs_yy} AS REAL) AS cvap_{acs_yyyy}_hispanic,
                CAST(cvap_aia{acs_yy} AS REAL) AS cvap_{acs_yyyy}_amind_aknative,
                CAST(cvap_asn{acs_yy} AS REAL) AS cvap_{acs_yyyy}_asian,
                CAST(cvap_blk{acs_yy} AS REAL) AS cvap_{acs_yyyy}_black,
                CAST(cvap_nhp{acs_yy} AS REAL) AS cvap_{acs_yyyy}_hawaii_pi,
                CAST(cvap_wht{acs_yy} AS REAL) AS cvap_{acs_yyyy}_nh_white,
                CAST(cvap_aiw{acs_yy} AS REAL) AS cvap_{acs_yyyy}_amind_aknative_white,
                CAST(cvap_asw{acs_yy} AS REAL) AS cvap_{acs_yyyy}_asian_white,
                CAST(cvap_blw{acs_yy} AS REAL) AS cvap_{acs_yyyy}_black_white,
                CAST(cvap_aib{acs_yy} AS REAL) AS cvap_{acs_yyyy}_amind_aknative_black,
                CAST(c_tot{acs_yy} AS REAL) AS cpop_{acs_yyyy}_total,
                CAST(c_nhs{acs_yy} AS REAL) AS cpop_{acs_yyyy}_nonhispanic,
                CAST(c_hsp{acs_yy} AS REAL) AS cpop_{acs_yyyy}_hispanic,
                CAST(c_aia{acs_yy} AS REAL) AS cpop_{acs_yyyy}_amind_aknative,
                CAST(c_asn{acs_yy} AS REAL) AS cpop_{acs_yyyy}_asian,
                CAST(c_blk{acs_yy} AS REAL) AS cpop_{acs_yyyy}_black,
                CAST(c_nhp{acs_yy} AS REAL) AS cpop_{acs_yyyy}_hawaii_pi,
                CAST(c_wht{acs_yy} AS REAL) AS cpop_{acs_yyyy}_nh_white,
                CAST(c_aiw{acs_yy} AS REAL) AS cpop_{acs_yyyy}_amind_aknative_white,
                CAST(c_asw{acs_yy} AS REAL) AS cpop_{acs_yyyy}_asian_white,
                CAST(c_blw{acs_yy} AS REAL) AS cpop_{acs_yyyy}_black_white,
                CAST(c_aib{acs_yy} AS REAL) AS cpop_{acs_yyyy}_amind_aknative_black,
                CAST(cvap_nhs{acs_yy} AS REAL) / NULLIF(CAST(cvap_tot{acs_yy} AS REAL), 0) AS pct_cvap_{acs_yyyy}_nonhispanic,
                CAST(cvap_hsp{acs_yy} AS REAL) / NULLIF(CAST(cvap_tot{acs_yy} AS REAL), 0) AS pct_cvap_{acs_yyyy}_hispanic,
                CAST(cvap_aia{acs_yy} AS REAL) / NULLIF(CAST(cvap_tot{acs_yy} AS REAL), 0) AS pct_cvap_{acs_yyyy}_amind_aknative,
                CAST(cvap_asn{acs_yy} AS REAL) / NULLIF(CAST(cvap_tot{acs_yy} AS REAL), 0) AS pct_cvap_{acs_yyyy}_asian,
                CAST(cvap_blk{acs_yy} AS REAL) / NULLIF(CAST(cvap_tot{acs_yy} AS REAL), 0) AS pct_cvap_{acs_yyyy}_black,
                CAST(cvap_nhp{acs_yy} AS REAL) / NULLIF(CAST(cvap_tot{acs_yy} AS REAL), 0) AS pct_cvap_{acs_yyyy}_hawaii_pi,
                CAST(cvap_wht{acs_yy} AS REAL) / NULLIF(CAST(cvap_tot{acs_yy} AS REAL), 0) AS pct_cvap_{acs_yyyy}_nh_white,
                CAST(cvap_aiw{acs_yy} AS REAL) / NULLIF(CAST(cvap_tot{acs_yy} AS REAL), 0) AS pct_cvap_{acs_yyyy}_amind_aknative_white,
                CAST(cvap_asw{acs_yy} AS REAL) / NULLIF(CAST(cvap_tot{acs_yy} AS REAL), 0) AS pct_cvap_{acs_yyyy}_asian_white,
                CAST(cvap_blw{acs_yy} AS REAL) / NULLIF(CAST(cvap_tot{acs_yy} AS REAL), 0) AS pct_cvap_{acs_yyyy}_black_white,
                CAST(cvap_aib{acs_yy} AS REAL) / NULLIF(CAST(cvap_tot{acs_yy} AS REAL), 0) AS pct_cvap_{acs_yyyy}_amind_aknative_black,
                CAST(c_nhs{acs_yy} AS REAL) / NULLIF(CAST(c_tot{acs_yy} AS REAL), 0) AS pct_cpop_{acs_yyyy}_nonhispanic,
                CAST(c_hsp{acs_yy} AS REAL) / NULLIF(CAST(c_tot{acs_yy} AS REAL), 0) AS pct_cpop_{acs_yyyy}_hispanic,
                CAST(c_aia{acs_yy} AS REAL) / NULLIF(CAST(c_tot{acs_yy} AS REAL), 0) AS pct_cpop_{acs_yyyy}_amind_aknative,
                CAST(c_asn{acs_yy} AS REAL) / NULLIF(CAST(c_tot{acs_yy} AS REAL), 0) AS pct_cpop_{acs_yyyy}_asian,
                CAST(c_blk{acs_yy} AS REAL) / NULLIF(CAST(c_tot{acs_yy} AS REAL), 0) AS pct_cpop_{acs_yyyy}_black,
                CAST(c_nhp{acs_yy} AS REAL) / NULLIF(CAST(c_tot{acs_yy} AS REAL), 0) AS pct_cpop_{acs_yyyy}_hawaii_pi,
                CAST(c_wht{acs_yy} AS REAL) / NULLIF(CAST(c_tot{acs_yy} AS REAL), 0) AS pct_cpop_{acs_yyyy}_nh_white,
                CAST(c_aiw{acs_yy} AS REAL) / NULLIF(CAST(c_tot{acs_yy} AS REAL), 0) AS pct_cpop_{acs_yyyy}_amind_aknative_white,
                CAST(c_asw{acs_yy} AS REAL) / NULLIF(CAST(c_tot{acs_yy} AS REAL), 0) AS pct_cpop_{acs_yyyy}_asian_white,
                CAST(c_blw{acs_yy} AS REAL) / NULLIF(CAST(c_tot{acs_yy} AS REAL), 0) AS pct_cpop_{acs_yyyy}_black_white,
                CAST(c_aib{acs_yy} AS REAL) / NULLIF(CAST(c_tot{acs_yy} AS REAL), 0) AS pct_cpop_{acs_yyyy}_amind_aknative_black
            FROM cvap_{acs_yyyy}_{src_table} cvap
            WHERE cvap.{geoid} = {table}{dec_yy}.geoid
        );
"""

insert_cvap_data_vtd = """
UPDATE vtd{dec_yy} 
    SET (
        cvap_{acs_yyyy}_total,
        cvap_{acs_yyyy}_nonhispanic,
        cvap_{acs_yyyy}_hispanic,
        cvap_{acs_yyyy}_amind_aknative,
        cvap_{acs_yyyy}_asian,
        cvap_{acs_yyyy}_black,
        cvap_{acs_yyyy}_hawaii_pi,
        cvap_{acs_yyyy}_nh_white,
        cvap_{acs_yyyy}_amind_aknative_white,
        cvap_{acs_yyyy}_asian_white,
        cvap_{acs_yyyy}_black_white,
        cvap_{acs_yyyy}_amind_aknative_black,
        cpop_{acs_yyyy}_total,
        cpop_{acs_yyyy}_nonhispanic,
        cpop_{acs_yyyy}_hispanic,
        cpop_{acs_yyyy}_amind_aknative,
        cpop_{acs_yyyy}_asian,
        cpop_{acs_yyyy}_black,
        cpop_{acs_yyyy}_hawaii_pi,
        cpop_{acs_yyyy}_nh_white,
        cpop_{acs_yyyy}_amind_aknative_white,
        cpop_{acs_yyyy}_asian_white,
        cpop_{acs_yyyy}_black_white,
        cpop_{acs_yyyy}_amind_aknative_black
    ) = (
        SELECT SUM(cvap_{acs_yyyy}_total) AS cvap_{acs_yyyy}_total,
            SUM(cvap_{acs_yyyy}_nonhispanic) AS cvap_{acs_yyyy}_nonhispanic,
            SUM(cvap_{acs_yyyy}_hispanic) AS cvap_{acs_yyyy}_hispanic,
            SUM(cvap_{acs_yyyy}_amind_aknative) AS cvap_{acs_yyyy}_amind_aknative,
            SUM(cvap_{acs_yyyy}_asian) AS cvap_{acs_yyyy}_asian,
            SUM(cvap_{acs_yyyy}_black) AS cvap_{acs_yyyy}_black,
            SUM(cvap_{acs_yyyy}_hawaii_pi) AS cvap_{acs_yyyy}_hawaii_pi,
            SUM(cvap_{acs_yyyy}_nh_white) AS cvap_{acs_yyyy}_nh_white,
            SUM(cvap_{acs_yyyy}_amind_aknative_white) AS cvap_{acs_yyyy}_amind_aknative_white,
            SUM(cvap_{acs_yyyy}_asian_white) AS cvap_{acs_yyyy}_asian_white,
            SUM(cvap_{acs_yyyy}_black_white) AS cvap_{acs_yyyy}_black_white,
            SUM(cvap_{acs_yyyy}_amind_aknative_black) AS cvap_{acs_yyyy}_amind_aknative_black,
            SUM(cpop_{acs_yyyy}_total) AS cpop_{acs_yyyy}_total,
            SUM(cpop_{acs_yyyy}_nonhispanic) AS cpop_{acs_yyyy}_nonhispanic,
            SUM(cpop_{acs_yyyy}_hispanic) AS cpop_{acs_yyyy}_hispanic,
            SUM(cpop_{acs_yyyy}_amind_aknative) AS cpop_{acs_yyyy}_amind_aknative,
            SUM(cpop_{acs_yyyy}_asian) AS cpop_{acs_yyyy}_asian,
            SUM(cpop_{acs_yyyy}_black) AS cpop_{acs_yyyy}_black,
            SUM(cpop_{acs_yyyy}_hawaii_pi) AS cpop_{acs_yyyy}_hawaii_pi,
            SUM(cpop_{acs_yyyy}_nh_white) AS cpop_{acs_yyyy}_nh_white,
            SUM(cpop_{acs_yyyy}_amind_aknative_white) AS cpop_{acs_yyyy}_amind_aknative_white,
            SUM(cpop_{acs_yyyy}_asian_white) AS cpop_{acs_yyyy}_asian_white,
            SUM(cpop_{acs_yyyy}_black_white) AS cpop_{acs_yyyy}_black_white,
            SUM(cpop_{acs_yyyy}_amind_aknative_black) AS cpop_{acs_yyyy}_amind_aknative_black
        FROM block{dec_yy}         
        WHERE vtd{dec_yy}.geoid = block{dec_yy}.vtdid
        GROUP BY vtdid
    );
UPDATE vtd{dec_yy} SET 
    pct_cvap_{acs_yyyy}_nonhispanic = cvap_{acs_yyyy}_nonhispanic / cvap_{acs_yyyy}_total,
    pct_cvap_{acs_yyyy}_hispanic = cvap_{acs_yyyy}_hispanic / cvap_{acs_yyyy}_total,
    pct_cvap_{acs_yyyy}_amind_aknative = cvap_{acs_yyyy}_amind_aknative / cvap_{acs_yyyy}_total,
    pct_cvap_{acs_yyyy}_asian = cvap_{acs_yyyy}_asian / cvap_{acs_yyyy}_total,
    pct_cvap_{acs_yyyy}_black = cvap_{acs_yyyy}_black / cvap_{acs_yyyy}_total,
    pct_cvap_{acs_yyyy}_hawaii_pi = cvap_{acs_yyyy}_hawaii_pi / cvap_{acs_yyyy}_total,
    pct_cvap_{acs_yyyy}_nh_white = cvap_{acs_yyyy}_nh_white / cvap_{acs_yyyy}_total,
    pct_cvap_{acs_yyyy}_amind_aknative_white = cvap_{acs_yyyy}_amind_aknative_white / cvap_{acs_yyyy}_total,
    pct_cvap_{acs_yyyy}_asian_white = cvap_{acs_yyyy}_asian_white / cvap_{acs_yyyy}_total,
    pct_cvap_{acs_yyyy}_black_white = cvap_{acs_yyyy}_black_white / cvap_{acs_yyyy}_total,
    pct_cvap_{acs_yyyy}_amind_aknative_black = cvap_{acs_yyyy}_amind_aknative_black / cvap_{acs_yyyy}_total,
    pct_cpop_{acs_yyyy}_nonhispanic = cpop_{acs_yyyy}_nonhispanic / cpop_{acs_yyyy}_total,
    pct_cpop_{acs_yyyy}_hispanic = cpop_{acs_yyyy}_hispanic / cpop_{acs_yyyy}_total,
    pct_cpop_{acs_yyyy}_amind_aknative = cpop_{acs_yyyy}_amind_aknative / cpop_{acs_yyyy}_total,
    pct_cpop_{acs_yyyy}_asian = cpop_{acs_yyyy}_asian / cpop_{acs_yyyy}_total,
    pct_cpop_{acs_yyyy}_black = cpop_{acs_yyyy}_black / cpop_{acs_yyyy}_total,
    pct_cpop_{acs_yyyy}_hawaii_pi = cpop_{acs_yyyy}_hawaii_pi / cpop_{acs_yyyy}_total,
    pct_cpop_{acs_yyyy}_nh_white = cpop_{acs_yyyy}_nh_white / cpop_{acs_yyyy}_total,
    pct_cpop_{acs_yyyy}_amind_aknative_white = cpop_{acs_yyyy}_amind_aknative_white / cpop_{acs_yyyy}_total,
    pct_cpop_{acs_yyyy}_asian_white = cpop_{acs_yyyy}_asian_white / cpop_{acs_yyyy}_total,
    pct_cpop_{acs_yyyy}_black_white = cpop_{acs_yyyy}_black_white / cpop_{acs_yyyy}_total,
    pct_cpop_{acs_yyyy}_amind_aknative_black = cpop_{acs_yyyy}_amind_aknative_black / cpop_{acs_yyyy}_total;
"""

add_vr_fields = """
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_total INTEGER;
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_party_democrat INTEGER;
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_party_republican INTEGER;
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_party_no_party INTEGER;
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_party_other INTEGER;
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_party_unknown INTEGER;
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_white INTEGER; --eth2_euro + eth2_34
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_hispanic INTEGER; --eth2__64
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_black INTEGER; --eth2_93 + eth2_99
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_asian INTEGER; --eth2_10 + eth2+23 + eth2_14 + eth2_12 + eth2_21
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_mena INTEGER; --eth2_30 + eth2_33 + eth2_32
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_amind_aknative INTEGER; --eth2_81
    ALTER TABLE {table}{dec_yy} ADD COLUMN reg_{vr_date}_unknown_race INTEGER; --eth2_unk
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_reg_{vr_date}_party_democrat REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_reg_{vr_date}_party_republican REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_reg_{vr_date}_party_no_party REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_reg_{vr_date}_party_other REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_reg_{vr_date}_party_unknown REAL;
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_reg_{vr_date}_white REAL; --eth2_euro + eth2_34
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_reg_{vr_date}_hispanic REAL; --eth2__64
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_reg_{vr_date}_black REAL; --eth2_93 + eth2_99
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_reg_{vr_date}_asian REAL; --eth2_10 + eth2+23 + eth2_14 + eth2_12 + eth2_21
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_reg_{vr_date}_mena REAL; --eth2_30 + eth2_33 + eth2_32
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_reg_{vr_date}_amind_aknative REAL; --eth2_81
    ALTER TABLE {table}{dec_yy} ADD COLUMN pct_reg_{vr_date}_unknown_race REAL; --eth2_unk
    """

insert_vr_data = """
UPDATE {table}{dec_yy}
    SET (
        reg_{vr_date}_total,
        reg_{vr_date}_party_democrat,
        reg_{vr_date}_party_republican,
        reg_{vr_date}_party_no_party,
        reg_{vr_date}_party_other,
        reg_{vr_date}_party_unknown,
        reg_{vr_date}_white, --eth2_euro + eth2_34
        reg_{vr_date}_hispanic, --eth2_64
        reg_{vr_date}_black, --eth2_93 + eth2_99
        reg_{vr_date}_asian, --eth2_10 + eth2_23 + eth2_14 + eth2_12 + eth2_21
        reg_{vr_date}_mena, --eth2_30 + eth2_33 + eth2_32
        reg_{vr_date}_amind_aknative, --eth2_81
        reg_{vr_date}_unknown_race, --eth2_unk
        pct_reg_{vr_date}_party_democrat,
        pct_reg_{vr_date}_party_republican,
        pct_reg_{vr_date}_party_no_party,
        pct_reg_{vr_date}_party_other,
        pct_reg_{vr_date}_party_unknown,
        pct_reg_{vr_date}_white, --eth2_euro + eth2_34
        pct_reg_{vr_date}_hispanic, --eth2__64
        pct_reg_{vr_date}_black, --eth2_93 + eth2_99
        pct_reg_{vr_date}_asian, --eth2_10 + eth2_23 + eth2_14 + eth2_12 + eth2_21
        pct_reg_{vr_date}_mena, --eth2_30 + eth2_33 + eth2_32
        pct_reg_{vr_date}_amind_aknative, --eth2_81
        pct_reg_{vr_date}_unknown_race --eth2_unk    
    ) = (
        SELECT 
            total_reg, 
            party_dem, 
            party_rep, 
            party_npp, 
            party_oth, 
            party_unk,
            eth2_euro + eth2_34, 
            eth2_64, 
            eth2_93 + eth2_99, 
            eth2_10 + eth2_23 + eth2_14 + eth2_12 + eth2_21,
            eth2_30 + eth2_33 + eth2_32, 
            eth2_81, 
            eth2_unk,
            CAST(party_rep AS REAL) / NULLIF(total_reg, 0),
            CAST(party_dem AS REAL) / NULLIF(total_reg, 0),
            CAST(party_npp AS REAL) / NULLIF(total_reg, 0),
            CAST(party_oth AS REAL) / NULLIF(total_reg, 0),
            CAST(party_unk AS REAL) / NULLIF(total_reg, 0),
            CAST(eth2_euro + eth2_34 AS REAL) / NULLIF(total_reg, 0),
            CAST(eth2_64 AS REAL) / NULLIF(total_reg, 0),
            CAST(eth2_93 + eth2_99 AS REAL) / NULLIF(total_reg, 0), 
            CAST(eth2_10 + eth2_23 + eth2_14 + eth2_12 + eth2_21 AS REAL) / NULLIF(total_reg, 0),
            CAST(eth2_30 + eth2_33 + eth2_32 AS REAL) / NULLIF(total_reg, 0), 
            CAST(eth2_81 AS REAL) / NULLIF(total_reg, 0),
            CAST(eth2_unk AS REAL) / NULLIF(total_reg, 0)
    FROM l2_{dec_yyyy}_{vr_date}_{src_table} vr
        WHERE vr.geoid20 = {table}{dec_yy}.geoid
    );
"""
