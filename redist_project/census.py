import os
import pathlib
import re
import shutil
import zipfile
from tempfile import mkdtemp
from typing import Union

import pandas as pd
import requests

from redist_project.geography import geographies
from redist_project.states import (
    StateCode,
    states
)

header_dict: dict[str, dict[str, type]] = {
    'Geoheader': {"FILEID": object, "STUSAB": object, "SUMLEV": object, "GEOVAR": object, "GEOCOMP": object, "CHARITER": object, "CIFSN": object, "LOGRECNO": object, "GEOID": object, "GEOCODE": object, "REGION": object, "DIVISION": object, "STATE": object, "STATENS": object, "COUNTY": object, "COUNTYCC": object, "COUNTYNS": object, "COUSUB": object, "COUSUBCC": object, "COUSUBNS": object, "SUBMCD": object, "SUBMCDCC": object, "SUBMCDNS": object, "ESTATE": object, "ESTATECC": object, "ESTATENS": object, "CONCIT": object, "CONCITCC": object, "CONCITNS": object, "PLACE": object, "PLACECC": object, "PLACENS": object, "TRACT": object, "BLKGRP": object, "BLOCK": object, "AIANHH": object, "AIHHTLI": object, "AIANHHFP": object, "AIANHHCC": object, "AIANHHNS": object, "AITS": object, "AITSFP": object, "AITSCC": object, "AITSNS": object, "TTRACT": object, "TBLKGRP": object, "ANRC": object, "ANRCCC": object, "ANRCNS": object, "CBSA": object, "MEMI": object, "CSA": object, "METDIV": object, "NECTA": object, "NMEMI": object, "CNECTA": object, "NECTADIV": object, "CBSAPCI": object, "NECTAPCI": object, "UA": object, "UATYPE": object, "UR": object, "CD116": object, "CD118": object, "CD119": object, "CD120": object, "CD121": object, "SLDU18": object, "SLDU22": object, "SLDU24": object, "SLDU26": object, "SLDU28": object, "SLDL18": object, "SLDL22": object, "SLDL24": object, "SLDL26": object, "SLDL28": object, "VTD": object, "VTDI": object, "ZCTA": object, "SDELM": object, "SDSEC": object, "SDUNI": object, "PUMA": object, "AREALAND": object, "AREAWATR": object, "BASENAME": object, "NAME": object, "FUNCSTAT": object, "GCUNI": object, "POP100": object, "HU100": object, "INTPTLAT": object, "INTPTLON": object, "LSADC": object, "PARTFLAG": object, "UGA": object},
    'Segment 1': {"FILEID": object, "STUSAB": object, "CHARITER": object, "CIFSN": object, "LOGRECNO": object, "P0010001": int, "P0010002": int, "P0010003": int, "P0010004": int, "P0010005": int, "P0010006": int, "P0010007": int, "P0010008": int, "P0010009": int, "P0010010": int, "P0010011": int, "P0010012": int, "P0010013": int, "P0010014": int, "P0010015": int, "P0010016": int, "P0010017": int, "P0010018": int, "P0010019": int, "P0010020": int, "P0010021": int, "P0010022": int, "P0010023": int, "P0010024": int, "P0010025": int, "P0010026": int, "P0010027": int, "P0010028": int, "P0010029": int, "P0010030": int, "P0010031": int, "P0010032": int, "P0010033": int, "P0010034": int, "P0010035": int, "P0010036": int, "P0010037": int, "P0010038": int, "P0010039": int, "P0010040": int, "P0010041": int, "P0010042": int, "P0010043": int, "P0010044": int, "P0010045": int, "P0010046": int, "P0010047": int, "P0010048": int, "P0010049": int, "P0010050": int, "P0010051": int, "P0010052": int, "P0010053": int, "P0010054": int, "P0010055": int, "P0010056": int, "P0010057": int, "P0010058": int, "P0010059": int, "P0010060": int, "P0010061": int, "P0010062": int, "P0010063": int, "P0010064": int, "P0010065": int, "P0010066": int, "P0010067": int, "P0010068": int, "P0010069": int, "P0010070": int, "P0010071": int, "P0020001": int, "P0020002": int, "P0020003": int, "P0020004": int, "P0020005": int, "P0020006": int, "P0020007": int, "P0020008": int, "P0020009": int, "P0020010": int, "P0020011": int, "P0020012": int, "P0020013": int, "P0020014": int, "P0020015": int, "P0020016": int, "P0020017": int, "P0020018": int, "P0020019": int, "P0020020": int, "P0020021": int, "P0020022": int, "P0020023": int, "P0020024": int, "P0020025": int, "P0020026": int, "P0020027": int, "P0020028": int, "P0020029": int, "P0020030": int, "P0020031": int, "P0020032": int, "P0020033": int, "P0020034": int, "P0020035": int, "P0020036": int, "P0020037": int, "P0020038": int, "P0020039": int, "P0020040": int, "P0020041": int, "P0020042": int, "P0020043": int, "P0020044": int, "P0020045": int, "P0020046": int, "P0020047": int, "P0020048": int, "P0020049": int, "P0020050": int, "P0020051": int, "P0020052": int, "P0020053": int, "P0020054": int, "P0020055": int, "P0020056": int, "P0020057": int, "P0020058": int, "P0020059": int, "P0020060": int, "P0020061": int, "P0020062": int, "P0020063": int, "P0020064": int, "P0020065": int, "P0020066": int, "P0020067": int, "P0020068": int, "P0020069": int, "P0020070": int, "P0020071": int, "P0020072": int, "P0020073": int},
    'Segment 2': {"FILEID": object, "STUSAB": object, "CHARITER": object, "CIFSN": object, "LOGRECNO": object, "P0030001": int, "P0030002": int, "P0030003": int, "P0030004": int, "P0030005": int, "P0030006": int, "P0030007": int, "P0030008": int, "P0030009": int, "P0030010": int, "P0030011": int, "P0030012": int, "P0030013": int, "P0030014": int, "P0030015": int, "P0030016": int, "P0030017": int, "P0030018": int, "P0030019": int, "P0030020": int, "P0030021": int, "P0030022": int, "P0030023": int, "P0030024": int, "P0030025": int, "P0030026": int, "P0030027": int, "P0030028": int, "P0030029": int, "P0030030": int, "P0030031": int, "P0030032": int, "P0030033": int, "P0030034": int, "P0030035": int, "P0030036": int, "P0030037": int, "P0030038": int, "P0030039": int, "P0030040": int, "P0030041": int, "P0030042": int, "P0030043": int, "P0030044": int, "P0030045": int, "P0030046": int, "P0030047": int, "P0030048": int, "P0030049": int, "P0030050": int, "P0030051": int, "P0030052": int, "P0030053": int, "P0030054": int, "P0030055": int, "P0030056": int, "P0030057": int, "P0030058": int, "P0030059": int, "P0030060": int, "P0030061": int, "P0030062": int, "P0030063": int, "P0030064": int, "P0030065": int, "P0030066": int, "P0030067": int, "P0030068": int, "P0030069": int, "P0030070": int, "P0030071": int, "P0040001": int, "P0040002": int, "P0040003": int, "P0040004": int, "P0040005": int, "P0040006": int, "P0040007": int, "P0040008": int, "P0040009": int, "P0040010": int, "P0040011": int, "P0040012": int, "P0040013": int, "P0040014": int, "P0040015": int, "P0040016": int, "P0040017": int, "P0040018": int, "P0040019": int, "P0040020": int, "P0040021": int, "P0040022": int, "P0040023": int, "P0040024": int, "P0040025": int, "P0040026": int, "P0040027": int, "P0040028": int, "P0040029": int, "P0040030": int, "P0040031": int, "P0040032": int, "P0040033": int, "P0040034": int, "P0040035": int, "P0040036": int, "P0040037": int, "P0040038": int, "P0040039": int, "P0040040": int, "P0040041": int, "P0040042": int, "P0040043": int, "P0040044": int, "P0040045": int, "P0040046": int, "P0040047": int, "P0040048": int, "P0040049": int, "P0040050": int, "P0040051": int, "P0040052": int, "P0040053": int, "P0040054": int, "P0040055": int, "P0040056": int, "P0040057": int, "P0040058": int, "P0040059": int, "P0040060": int, "P0040061": int, "P0040062": int, "P0040063": int, "P0040064": int, "P0040065": int, "P0040066": int, "P0040067": int, "P0040068": int, "P0040069": int, "P0040070": int, "P0040071": int, "P0040072": int, "P0040073": int, "H0010001": int, "H0010002": int, "H0010003": int},
    'Segment 3': {"FILEID": object, "STUSAB": object, "CHARITER": object, "CIFSN": object, "LOGRECNO": object, "P0050001": int, "P0050002": int, "P0050003": int, "P0050004": int, "P0050005": int, "P0050006": int, "P0050007": int, "P0050008": int, "P0050009": int, "P0050010": int},
}

HOST = os.environ["CENSUS_API_URL"]
CENSUS_API_KEY = os.environ["CENSUS_API_KEY"]

pl_groups = [
    "H1",
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
]

pl_non_group_fields = [
    "AIANHH",
    "AIHHTL",
    "AIRES",
    "ANRC",
    "BLKGRP",
    "BLOCK",
    "CBSA",
    "CD",
    "CNECTA",
    "CONCIT",
    "COUNTY",
    "COUSUB",
    "CSA",
    "DIVISION",
    "GEOCOMP",
    "METDIV",
    "NATION",
    "NECTA",
    "NECTADIV",
    "PLACE",
    "PLACEREM",
    "REGION",
    "SDELM",
    "SDSEC",
    "SDUNI",
    "SLDL",
    "SLDU",
    "STATE",
    "SUBMCD",
    "SUMLEVEL",
    "TRACT",
    "TRISUBREM",
    "VTD",
]


URLS = {
    "2020": {
        "field_def": "https://www2.census.gov/programs-surveys/decennial/rdo/about/{year}-census-program/Phase3/SupportMaterials/{year}_PLSummaryFile_FieldNames.xlsx",
        "baf": "https://www2.census.gov/geo/docs/maps-data/data/baf{year}/BlockAssign_ST{fips}_{st}.zip",
        "pl_data": "https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/{state}/{st}{year}.pl.zip",
        "shape": "https://www2.census.gov/geo/tiger/TIGER2020PL/STATE/{fips}_{state_caps}/{fips}/tl_{year}_{fips}_{{geog}}{yy}.zip"
    },
    "2010": {
        "field_def": "https://www2.census.gov/census_{year}/01-Redistricting_File--PL_94-171/0FILE_STRUCTURE.doc",
        "baf": "https://www2.census.gov/geo/docs/maps-data/data/baf/BlockAssign_ST{fips}_{st_caps}.zip",
        "pl_data": "https://www2.census.gov/census_{year}/01-Redistricting_File--PL_94-171/{state}/{st}{year}.pl.zip",
        "shape": "https://www2.census.gov/geo/pvs/tiger{year}st/{fips}_{state}/{fips}/tl_{year}_{fips}_tabblock{yy}.zip"
    }
}


def download(url, dest_path: pathlib.Path):
    if not url:
        return None

    r = requests.get(url, allow_redirects=True, timeout=60)
    if not r.ok:
        return None

    cd = r.headers.get('content-disposition')
    if cd:
        fname = re.findall('filename=(.+)', cd)
    else:
        fname = url.rsplit('/', 1)[1]

    file_path: pathlib.Path = dest_path / fname

    with (file_path).open('w+') as f:
        f.write(r.content)

    return file_path


def download_decennial(st: str, dec_year: str = "2020", dest_path: pathlib.Path = None):
    if dest_path is None:
        dest_path = pathlib.Path(mkdtemp())

    for f, urlt in URLS[dec_year].items():
        url = urlt.format(
            st=st,
            year=dec_year,
            yy=dec_year[2:],
            state=states[st].name,
            state_caps=states[st].name.upper(),
            st_caps=st.upper(),
            fips=states[st].fips
        )

        if f == "shape":
            for geog in geographies:
                g_url = url.format(geog=geographies[geog].shp)
                p = download(g_url, dest_path)
        else:
            p = download(url, dest_path)

    for p in dest_path.iterdir():
        if p.suffix == '.zip':
            with zipfile.ZipFile(p, "r") as z:
                zpath = dest_path / f
                z.extractall(zpath)

    return dest_path


def get_2020pl_data(st_fips, cty_fips=None, geog="b", year="2020", variables: str | list[str] = None, groups: str | list[str] = None):
    dataset = "dec/pl"
    base_url = "/".join([HOST, year, dataset])

    if isinstance(variables, str):
        variables = [variables]

    if isinstance(groups, str):
        groups = [groups]

    params = {"key": CENSUS_API_KEY}
    if geog == 'b':
        params["for"] = "block:*"
    elif geog == 'bg':
        params["for"] = "block group:*"
    else:
        params["for"] = f"{geog}:*"

    params["in"] = f"state:{st_fips}"
    if cty_fips and geog != "county":
        params["in"] += f"+county:{cty_fips}"

    if variables is not None:
        params["get"] = ','.join(variables)
    elif groups is None:
        params["get"] = ','.join(pl_non_group_fields)

    if "get" in params:
        r = requests.get(base_url, params=params)
        col_names = r.json()[0]
        data = r.json()[1:]
        pop_data = pd.DataFrame(columns=col_names, data=data, index="GEO_ID")
    else:
        pop_data = None

    if groups:
        for g in groups:
            if not g in pl_groups:
                # log error
                continue
            params["get"] = f"group({g})"
            r = requests.get(base_url, params=params)
            col_names = r.json()[0]
            data = r.json()[1:]
            if pop_data:
                pop_data.join(pd.DataFrame(columns=col_names,
                              data=data, index="GEO_ID", dtype=int))
            else:
                pop_data = pd.DataFrame(
                    columns=col_names, data=data, index="GEO_ID")

    if pop_data and geog == 'b':
        pop_data["block group"] = pop_data["block"].apply(lambda x: x[0])

    return pop_data


def download_pldata(st: StateCode, year: str, dest_path: Union[str, pathlib.Path] = None):
    if not dest_path:
        dest_path = pathlib.Path(mkdtemp())
    elif not isinstance(dest_path, pathlib.Path):
        dest_path - pathlib.Path(dest_path)

    url = states[st].pl_url(year)
    if not url:
        return None
    r = requests.get(url, allow_redirects=True, timeout=60)
    if not r.ok:
        return None

    cd = r.headers.get('content-disposition')
    if cd:
        fname = re.findall('filename=(.+)', cd)
    else:
        fname = url.rsplit('/', 1)[1]

    file_path: pathlib.Path = dest_path / fname

    with (file_path).open('w+') as f:
        f.write(r.content)

    return file_path


def download_acs_data(st: StateCode, year: str, dest_path: Union[str, pathlib.Path] = None):
    if not dest_path:
        dest_path = pathlib.Path(mkdtemp())
    elif not isinstance(dest_path, pathlib.Path):
        dest_path - pathlib.Path(dest_path)

    url = states[st].acs_url(year)
    if not url:
        return None
    r = requests.get(url, allow_redirects=True, timeout=60)
    if not r.ok:
        return None

    cd = r.headers.get('content-disposition')
    if cd:
        fname = re.findall('filename=(.+)', cd)
    else:
        fname = url.rsplit('/', 1)[1]

    file_path: pathlib.Path = dest_path / fname

    with (file_path).open('w+') as f:
        f.write(r.content)

    return file_path


def download_shapefile(st: StateCode, year: str, geog: str, dest_path: Union[str, pathlib.Path] = None):
    if not dest_path:
        dest_path = pathlib.Path(mkdtemp())
    elif not isinstance(dest_path, pathlib.Path):
        dest_path - pathlib.Path(dest_path)

    base_url = states[st].shapefile_url(year)
    url = f"{base_url}/{geographies[geog]['shp']}"
    r = requests.get(url, allow_redirects=True, timeout=60)
    if not r.ok:
        return None

    cd = r.headers.get('content-disposition')
    if cd:
        fname = re.findall('filename=(.+)', cd)
    else:
        fname = url.rsplit('/', 1)[1]

    file_path: pathlib.Path = dest_path / fname

    with (file_path).open('w+') as f:
        f.write(r.content)

    return file_path


def download_fielddef(dest_path: Union[str, pathlib.Path] = None):
    if not dest_path:
        dest_path = pathlib.Path(mkdtemp())
    elif not isinstance(dest_path, pathlib.Path):
        dest_path - pathlib.Path(dest_path)

    url = "https://www2.census.gov/programs-surveys/decennial/rdo/about/2020-census-program/Phase3/SupportMaterials/2020_PLSummaryFile_FieldNames.xlsx"
    r = requests.get(url, allow_redirects=True, timeout=60)
    if not r.ok:
        return None

    cd = r.headers.get('content-disposition')
    if cd:
        fname = re.findall('filename=(.+)', cd)[0]
    else:
        fname = url.rsplit('/', 1)[1]

    file_path: pathlib.Path = dest_path / fname

    with (file_path).open('w+') as f:
        f.write(r.content)

    return file_path


def copy_metadata(readme_path, zip_name, dtype, wd):
    dest = '_'.join(['readme', zip_name, dtype])
    dest = '.'.join([dest, 'txt'])
    readmes = os.path.join(wd, 'READMES')
    if not os.path.exists(readmes):
        os.mkdir(readmes)
    shp_readmes = os.path.join(readmes, 'SHP')
    if not os.path.exists(shp_readmes):
        os.mkdir(shp_readmes)
    csv_readmes = os.path.join(readmes, 'CSV')
    if not os.path.exists(csv_readmes):
        os.mkdir(csv_readmes)
    if dtype == 'shp':
        dest_path = os.path.join(shp_readmes, dest)
        shutil.copy(readme_path, dest_path)
    if dtype == 'csv':
        dest_path = os.path.join(csv_readmes, dest)
        shutil.copy(readme_path, dest_path)


def write_readme(readme_path: pathlib.Path, zip_name, st, geog, dtype):
    state_name = states[st].name  # get full name of the state
    geog_full = geographies[geog].name  # get full geography name
    list_of_sections = [
        'Redistricting Data Hub (RDH) Retrieval Date', 'Sources', 'Fields', 'Processing', 'Additional Notes']
    new_section = '\n'+'\n'+'##'
    header_section = '2020 PL 94-171 Data Summary File for ' + state_name + \
        ' based on the Decennial Census at the ' + geog_full + ' level'
    if dtype == 'shp':
        header_section = header_section + \
            ' on 2020 Census Redistricting Data (P.L. 94-171) Shapefiles'
    header_section = header_section + '\n' + '\n' + 'Please note that we have NOT validated against the official data used by your state’s redistricting body or bodies. Some states reallocate incarcerated persons and/or exclude non-permanent residents from the PL 94-171 data file for redistricting. Other states may make additional modifications. For more information about state modifications, visit our PL 94-171 Modifications article included in https://redistrictingdatahub.org/data/about-our-data/'
    if geog in ['sldu', 'sldl', 'cd']:
        header_section = header_section + '\n' + '\n' + "Please note that the Census Bureau does not account for changes to congressional, and state legislative district boundaries since the 2018 election. For more information, contact your state's redistricting body or check out All About Redistricting https://redistricting.lls.edu/"
    date_section = new_section + list_of_sections[0] + '\n' + '08/12/21'
    sources_section = new_section + \
        list_of_sections[1] + '\n' + '2020 PL 94-171 Legacy Format Data was retrieved from the US Census FTP site https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/'
    if dtype == 'shp':
        sources_section = sources_section + '\n' + \
            '2020 Census Redistricting Data (P.L. 94-171) Shapefiles were retrieved on 05/24/21 from https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html'
    fields_section = new_section + \
        list_of_sections[2] + '\n' + \
        'For a full list of fields and descriptions, review the 2020 Census State Redistricting Data (Public Law 94-171) Summary File Technical Documentation at https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/summary-file/2020Census_PL94_171Redistricting_StatesTechDoc_English.pdf'
    process_section = new_section + \
        list_of_sections[3] + '\n' + 'The legacy format 2020 PL 94-171 Data was downloaded from the Census. \nThe legacy format data is provided in one zip file per state. Each zip file contains four files: 3 “segments” containing the data for 1 or more standard redistricting tables, and 1 “geographic header” file. \nThe first segment contains the data for Tables P1 (Race) and P2 (Hispanic or Latino, and Not Hispanic or Latino by Race). The second segment contains data for Tables P3 (Race for the Population 18 Years and Over), P4 (Hispanic or Latino, and Not Hispanic or Latino by Race for the Population 18 Years and Over), and H1 (Occupancy Status). The third segment contains Table P5 (Group Quarters Population by Major Group Quarters Type), which was not part of the 2010 PL 94-171 data release.\nThe files were imported into Python as pipe-delimited data frames and the columns renamed. The segments were joined together and then to the geo file, using the logical record number, or LOGRECNO.\nThe 10 different summary levels that the RDH processed were queried from the data, each corresponding to a particular unit of geography: state, county, tract, block group, block, congressional district, state legislative district - lower, state legislative district - upper, minor civil division, and census place.\nThen the corresponding geographies were merged with the 2020 Census Redistricting Data (P.L. 94-171) shapefiles based on Census GEOIDs. \nFinally, the tabulated data were exported in CSV and shapefile formats.\nThe RDH verified results internally and externally with partner organizations. \nFor additional processing information, review our GitHub https://github.com/nonpartisan-redistricting-datahub'
    if dtype == 'shp':
        # this section deals with two dataset where the number of cases in the CSV and SHP do not align
        if str(zip_name).endswith('wv_pl2020_vtd'):
            add_section = new_section + \
                list_of_sections[4] + \
                "Note that in our validation of this file we found a mismatch between the VTD CSV and SHP length. List of missing GEOIDs in the final joined shapefile are:{'54009000000', '54077000000', '54033000000', '54051000000', '54063000000', '54049000000', '54055000000', '54027000000', '54081000000', '54065000000', '54039000000', '54047000000', '54107000000'}"
            add_section = add_section + '\n' + '\nFor more information about this data set, visit our PL 94-171 article included in https://redistrictingdatahub.org/data/about-our-data/. \n\nFor additional questions, email info@redistrictingdatahub.org.'
        if str(zip_name).endswith('me_pl2020_vtd'):
            add_section = new_section + \
                list_of_sections[4] + \
                "Note that in our validation of this file we found a mismatch between the VTD CSV and SHP length. List of missing GEOIDs in the final joined shapefile are: {'23021000000', '23025000000', '23007000000', '23013000000', '23003000000', '23019000000', '23017000000', '23029000000', '23009000000', '23015000000'}"
            add_section = add_section + '\n' + '\nFor more information about this data set, visit our PL 94-171 article included in https://redistrictingdatahub.org/data/about-our-data/. \n\nFor additional questions, email info@redistrictingdatahub.org.'
        else:
            add_section = new_section + \
                list_of_sections[4] + '\n' + 'For more information about this data set, visit our PL 94-171 article included in https://redistrictingdatahub.org/data/about-our-data/. \n\nFor additional questions, email info@redistrictingdatahub.org.'
    else:
        add_section = new_section + \
            list_of_sections[4] + '\n' + 'For more information about this data set, visit our PL 94-171 article included in https://redistrictingdatahub.org/data/about-our-data/. \n\nFor additional questions, email info@redistrictingdatahub.org.'
    to_write = header_section + date_section + sources_section + \
        fields_section + process_section + add_section
    to_write = str(to_write)
    with open(readme_path, 'w') as metadata:
        metadata.write(to_write)
    copy_metadata(readme_path, zip_name, dtype, readme_path.parent)


def zip_folder(name, readme_path: pathlib.Path, list_of_file_paths: list[pathlib.Path], dtype):
    dir_path = list_of_file_paths[0].resolve().parent
    root = dir_path
    # instantiate the zip object
    zipObj = zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED)
    readme = readme_path
    readme_dir = readme.parent
    readme_root = readme.resolve().parent
    zipObj.write(readme, readme.relative_to(readme_root))
    if dtype == 'csv':
        for i in list_of_file_paths:
            zipObj.write(i, i.relative_to(root))
        zipObj.close()
        for i in list_of_file_paths:
            i.unlink()
    if dtype == 'shp':
        for i in list_of_file_paths:
            basename = i.resolve().name
            basename = basename.split('.')[0]
            dir_path = i.resolve().parent
            cpg_path = dir_path / (basename+'.cpg')
            dbf_path = dir_path / (basename+'.dbf')
            prj_path = dir_path / (basename+'.prj')
            shx_path = dir_path / (basename+'.shx')
            zipObj.write(i, i.relative_to(root))
            if cpg_path.exists():
                zipObj.write(cpg_path, cpg_path.relative_to(root))
            if dbf_path.exists():
                zipObj.write(dbf_path, os.path.relpath(dbf_path, root))
            if prj_path.exists():
                zipObj.write(prj_path, os.path.relpath(prj_path, root))
            if shx_path.exists():
                zipObj.write(shx_path, os.path.relpath(shx_path, root))
        zipObj.close()
        for i in list_of_file_paths:
            basename = i.resolve().name
            basename = basename.split('.')[0]
            dir_path = i.resolve().parent
            cpg_path = dir_path / (basename+'.cpg')
            dbf_path = dir_path / (basename+'.dbf')
            prj_path = dir_path / (basename+'.prj')
            shx_path = dir_path / (basename+'.shx')
            i.unlink()
            if cpg_path.exists():
                cpg_path.unlink()
            if dbf_path.exists():
                dbf_path.unlink()
            if prj_path.exists():
                prj_path.unlink()
            if shx_path.exists():
                shx_path.unlink()
    shutil.rmtree(readme_dir)


def get_shape(fips, level, shp_dict: dict[str, list[pathlib.Path]]):
    for k, v in shp_dict.items():  # for each item in the dictionary defined above
        if level == k:  # if the level input matchs the key
            # for each file path (i) that is avaiable for that geography (v is a list)
            for i in v:
                basepath = i.resolve().name  # get the basebath
                fips_match = basepath.split('_')[2]
                if fips == fips_match:  # if the FIPS input matches the fips code in the tract
                    return i  # return the filepath from the list (v)
                else:
                    continue
        else:
            continue


BEQ_URL = "https://www2.census.gov/geo/docs/maps-data/data/baf{year}/BlockAssign_ST{fips}_{st}.zip"


def get_block_assignments(st, level, dec_year):
    y = "" if dec_year == "2010" else dec_year
    url = BEQ_URL.format(year=y, st=st, fips=states[st].fips)
    r = requests.get(url, headers={"accept": "application/zip"}, timeout=300)


def process_pl_data(st: str, year: str, path: pathlib.Path):
    # Identify the full paths for all files in the state's folder
    seg1_path = path / f'{st}000012020.pl'
    seg2_path = path / f'{st}000022020.pl'
    seg3_path = path / f'{st}000032020.pl'
    geo_path = path / f'{st}geo2020.pl'
    # Read in all file files from their full path

    # each segment should read in the column names from the header_dict and the data types given the dtype header dict
    seg1 = pd.read_csv(
        seg1_path,
        delimiter='|',
        header=None,
        names=header_dict['Segment 1'].keys(),
        dtype=header_dict['Segment 1'],
        index_col="LOGRECNO"
    )
    seg2 = pd.read_csv(
        seg2_path,
        delimiter='|',
        header=None,
        names=header_dict['Segment 2'].keys(),
        dtype=header_dict['Segment 2'],
        index_col="LOGRECNO"
    )
    seg3 = pd.read_csv(
        seg3_path,
        delimiter='|',
        header=None,
        names=header_dict['Segment 3'].keys(),
        dtype=header_dict['Segment 3'],
        index_col="LOGRECNO"
    )

    try:
        geo = pd.read_csv(
            geo_path,
            delimiter='|',
            header=None,
            names=header_dict['Geoheader'].keys(),
            dtype=header_dict['Geoheader'],
        )
    except:
        # the exception is used to deal with particular characters that may appear in some City, VTD, County, or other names, such as ~
        geo = pd.read_csv(
            geo_path,
            delimiter='|',
            header=None,
            names=header_dict['Geoheader'].keys(),
            dtype=header_dict['Geoheader'],
            encoding='latin-1'
        )

    # Identify columns to removed from the segments (as to not replicate in the join)
    drop_cols = ['FILEID', 'STUSAB', 'CHARITER', 'CIFSN']
    geo.drop(columns=['CIFSN'], inplace=True)
    seg1.drop(columns=drop_cols, inplace=True)
    seg2.drop(columns=drop_cols, inplace=True)
    seg3.drop(columns=drop_cols, inplace=True)

    # Create GEOID field for the merge to the shapefiles later
    geo['GEOID'] = geo['GEOID'].astype(str)
    geo['GEOID20'] = geo['GEOID'].apply(lambda x: x.split('US', maxsplit=1)[1])

    full_pl = geo.join([seg1, seg2, seg3], on='LOGRECNO')

    # Assign FIPS from the state abbreviation

    state_sums = []
    cols4comp = []
    # for each item in the geography dictionary, process the data
    # NOTE: This code works for validation *if* the geography for State (040) is listed first.
    for geog, g in geographies.items():
        sum_lev = g.level
        unique_sum_levs = list(full_pl['SUMLEV'].unique())
        if sum_lev not in unique_sum_levs:
            # warn: THERE IS NO DATA AT THIS LEVEL FOR [st]
            continue

        sumlev_pl = full_pl[full_pl['SUMLEV'] == sum_lev].copy()
        len_queried = len(sumlev_pl)

        # drop any columns that may have entirely null data (this happens as not all GEOHEADER fields are applicable to all geographies)
        cols_to_drop = []
        for i in list(sumlev_pl.columns):
            null_sum = int(sumlev_pl[i].isnull().sum())
            if null_sum == int(len(sumlev_pl)):
                cols_to_drop.append(i)

        sumlev_pl = sumlev_pl.drop(columns=cols_to_drop)
        sumlev_pl.dropna(axis=1, how='all')

        # Organize and set up folders for extraction
        file_name = '_'.join([st, 'pl2020', geog])
        csv_folder = out_path / "CSV"
        if csv_folder.exists():
            csv_folder.mkdir()

        lev_csv = '_'.join([geog, 'csv'])
        lev_csv_folder = csv_folder / lev_csv
        if not lev_csv_folder.exists():
            lev_csv_folder.mkdir()
        file_path = lev_csv_folder / file_name+'.csv'
        if len(sumlev_pl) == 0:
            # LENGTH OF CSV IS 0 SO THERE IS NO DATA AVAILABLE AT THIS LEVEL FOR THIS STATE.
            continue
        sumlev_pl.to_csv(file_path, index=False)

        # start the process of zipping the CSVs
        zip_name = file_name+'.zip'
        zip_path = lev_csv_folder / zip_name
        new_readme_holder = lev_csv_folder / 'README_HOLD_'+st
        if not new_readme_holder.exists():
            new_readme_holder.mkdir()
        readme_path = new_readme_holder / 'README.txt'
        zip_name = zip_name.split('.')[0]
        write_readme(readme_path, zip_name, st, geog, 'csv')
        file_paths_list = [file_path]
        zip_folder(zip_path, readme_path, file_paths_list, 'csv')

        # start the process for Shapefiles
        shp_folder = out_path / 'SHP'
        if not shp_folder.exists():
            shp_folder.mkdir()
        lev_shp = '_'.join([geog, 'shp'])
        lev_shp_folder = shp_folder / lev_shp
        if not lev_shp_folder.exists():
            lev_shp_folder.mkdir()

        # get the shapefile path
        shp_path = get_shp(states[st].fips, geog, shp_dict)

        if shp_path is not None:
            write_output('Reading in shapefile for '+sa.upper() +
                         ' at the '+geog + ' level..', sa)

            # read in the shapefile with no rows to get the columns and set the datatypes, then read in again
            shp_geog = gp.read_file(shp_path, rows=0)
            shp_geog_cols = list(shp_geog.columns)
            int_cols = ['ALAND20', 'AWATER20']
            temp_dict = {}
            for col_name in shp_geog_cols:
                if col_name in int_cols:
                    temp_dict[col_name] = 'int'
                else:
                    temp_dict[col_name] = 'object'

            shp_geog = gp.read_file(shp_path, dtype=temp_dict)

            # remove columns that may be entirely null
            cols_to_drop = []
            for i in list(shp_geog.columns):
                null_sum = int(shp_geog[i].isnull().sum())
                if null_sum == int(len(shp_geog)):
                    cols_to_drop.append(i)
            shp_geog = shp_geog.drop(columns=cols_to_drop)
            shp_geog.dropna(axis=1, how='all')

            # merge the shapefile and PL data
            write_output('SHP GEOG', sa)
            write_output('Merging data and shapefiles...', sa)
            match = len(shp_geog) == len_queried
            if match == True:
                write_output(
                    'There are the same number of rows in the shapefile and the PL data.', sa)
            else:
                write_output(
                    'There are NOT the same number of rows in the shapefile and the PL data.', sa)
                write_output('There are ' + str(len(shp_geog)) +
                             ' rows in the shapefile.', sa)
                write_output('There are '+str(len(sumlev_pl)
                                              ) + ' row in the PL data.', sa)
            write_output('Merging shapefile and joined segments...', sa)

            geo1_2_3 = pd.merge(shp_geog, sumlev_pl, on='GEOID20')
            write_output('Done merging data and shapefiles.', sa)
            write_output('JOINED SHP AND DATA', sa)

            file_path = os.path.join(lev_shp_folder, file_name+'.shp')
            list_of_shp_lens = [len_queried, len(shp_geog), len(geo1_2_3)]
            set_shp_lens = set(list_of_shp_lens)
            # confirm that the shapefile is the same length as the queried PL data
            if len(set_shp_lens) == 1:
                write_output(
                    'THE QUERIED DATA, SHAPEFILE, AND CREATED GEODATAFRAME ARE ALL THE SAME LENGTH WHICH IS '+str(len(shp_geog)), sa)
            else:
                write_output(
                    'THE QUERIED DATA, SHAPEFILE, AND CREATE GEODATAFRAME ARE NOT ALL THE SAME LENGHT.', sa)
            write_output('Making SHPs at the '+geog +
                         ' level for ' + sa.upper(), sa)
            # extract the shapefile
            geo1_2_3.to_file(file_path)
            write_output('Join shapefile and data complete', sa)

            file_paths_list = [file_path]
            zip_name = file_name+'.zip'
            zip_path = os.path.join(lev_shp_folder, zip_name)
            zip_name = zip_name.split('.')[0]

            # Write meta-data
            new_readme_holder = os.path.join(lev_shp_folder, 'README_HOLD_'+sa)
            if not os.path.exists(new_readme_holder):
                os.mkdir(new_readme_holder)
            readme_path = os.path.join(new_readme_holder, 'README.txt')
            write_readme(readme_path, zip_name, sa, geog, 'shp')
            write_output('Starting to zip SHPs..', sa)
            zip_folder(zip_path, readme_path, file_paths_list, 'shp')
            write_output('SHP ZIP FOLDER COMPLETE', sa)
        else:
            write_output('There is no shapefile available at the ' +
                         geog + ' for '+sa.upper(), sa)
            write_output(k.upper() + " files for "+sa.upper()+" were processed in " +
                         "--- %s seconds ---" % (time.time() - geog_start_time), sa)
            continue
        write_output(k.upper() + " files for " + sa.upper() + " were processed in " +
                     "--- %s seconds ---" % (time.time() - geog_start_time), sa)
    state_end_time = time.time()
    diff_sec = state_end_time - state_start_time
    diff_min = diff_sec/60
    diff_hr = diff_min/60
    write_output('\nTotal time difference (minutes) for ' +
                 sa.upper()+': '+str(diff_min), sa)
    write_output('Total time difference (hours) for ' +
                 sa.upper()+': '+str(diff_hr), sa)
    completed_raw_pl = os.path.join(wd, 'completed-raw-pl')
    if not os.path.exists(completed_raw_pl):
        os.mkdir(completed_raw_pl)
    new_state_folder_path = os.path.join(completed_raw_pl, state_folder_name)
    shutil.move(state_folder, new_state_folder_path)
    progress_output(sa, diff_hr, diff_min, tracker_path=tracker_path)
