# -*- coding: utf-8 -*-
"""Redistricting Project Generator 

    Generate projects for the QGIS Redistricting Plugin 
    from standardized redistricting datasets

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
import datetime
import itertools
import logging
import pathlib
import sys
import urllib.parse
from collections.abc import (
    Callable,
    Generator,
    Iterable,
    Iterator
)
from email.utils import parsedate_to_datetime
from typing import (
    Any,
    TypeVar,
    Union
)

import requests
from bs4 import BeautifulSoup
from qgis.core import (
    Qgis,
    QgsMessageLog
)
from qgis.gui import QgisInterface
from qgis.utils import iface
from redistricting.utils import \
    spatialite_connect  # pylint: disable=unused-import

iface: QgisInterface


_T = TypeVar("_T")

if sys.version_info > (3, 12):
    from itertools import batched  # pylint: disable=unused-import
else:
    def batched(iterable: Iterable[_T], chunk_size) -> Generator[tuple[_T, ...], Any, None]:
        if isinstance(iterable, Iterator):
            iterator = iterable
        else:
            iterator = iter(iterable)
        while chunk := tuple(itertools.islice(iterator, chunk_size)):
            yield chunk


def cvap_years(year):
    # census ftp is too unreliable, so scrape available cvap years from html
    url = "https://www2.census.gov/programs-surveys/decennial/rdo/datasets"
    r = requests.get(url, allow_redirects=True, timeout=10)
    if not r.ok:
        QgsMessageLog.logMessage("Could not retrieve CVAP data", "Warning", Qgis.Warning)
        iface.messageBar().pushWarning("Warning", "Could not retrieve CVAP data")

    years = {}
    s = BeautifulSoup(r.content)
    table = s.find("table")  # the table element is
    contents = [row.find_all("td")[1].get_text()[:-1] for row in table.find_all("tr")[3:-1]]

    for y in contents:
        if int(y) >= int(year):
            years[y] = f"{url}/{y}/{y}-cvap/CVAP_{int(y)-4}-{y}_csv_files.zip"

    return years


def null_progress(_: Union[int, float]):
    ...


def partial_progress(start, end, progress: Callable[[Union[int, float]], None] = None):
    def prog(f: float):
        progress(start + f * (end - start) / 100)

    return prog if progress is not None and progress is not null_progress else null_progress


def check_cache(url: str, cached_file_path: pathlib.Path) -> bool:
    r = requests.head(url, allow_redirects=True, timeout=60)
    if r.ok:
        if cached_file_path.exists():
            if "last-modified" in r.headers:
                mod_date = parsedate_to_datetime(r.headers["last-modified"])
                if mod_date <= datetime.datetime.fromtimestamp(cached_file_path.stat().st_ctime, tz=datetime.timezone.utc):
                    return True

            cached_file_path.unlink()
    else:
        logging.error("Failed to head %s", url)

    return False


def download(
    url: str,
    dest_path: pathlib.Path,
    progress: Callable[[Union[int, float]], None] = null_progress,
    tries: int = 1
):
    while tries > 0:
        try:
            r = requests.get(url, allow_redirects=True, timeout=60, stream=True)
            if not r.ok:
                if r.status_code == 404:
                    return False

                raise r.raise_for_status()

            total = int(r.headers.get("content-length", 0)) or 1
            count = 0

            block_size = 4096
            with dest_path.open('wb+') as file:
                for data in r.iter_content(block_size):
                    if total != 1:
                        count += len(data)
                        progress(100 * count // total)
                    file.write(data)

            break
        except TimeoutError:
            tries -= 1
            if tries == 0:
                raise
            continue

    progress(100)

    return True


def check_download(url: str, dest: pathlib.Path, progress: Callable[[Union[int, float]], None] = None):
    file_path = dest / pathlib.Path(urllib.parse.urlparse(url).path).name
    if not check_cache(url, file_path):
        if not download(url, file_path, progress):
            return None

    return file_path
