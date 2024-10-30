# -*- coding: utf-8 -*-
"""QGIS Redistricting Project Plugin - data package download

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
from typing import TYPE_CHECKING

import requests
from qgis.core import (
    QgsFeedback,
    QgsTask
)

from ._debug import debug_thread
from .settings import settings
from .state import geopackage_name

if TYPE_CHECKING:
    from .state import State


def download(state: "State", progress: QgsFeedback = None):
    gpkg_name = geopackage_name(state)
    url = f"https://redist-data.s3.amazonaws.com/{state.year}/{gpkg_name}"

    r = requests.get(url, allow_redirects=True, timeout=60, stream=True)
    if not r.ok:
        return None

    file_path = settings.datapath / gpkg_name

    total = int(r.headers.get("content-length", 0))
    count = 0
    block_size = 4096
    with file_path.open("wb+") as file:
        for data in r.iter_content(block_size):
            count += block_size
            if progress:
                progress.setProgress(100*count/total)
            file.write(data)

    return file_path


class StateDownloadTask(QgsTask):
    def __init__(self, state: "State"):
        super().__init__(f"Downloading {geopackage_name(state)}")
        self.state = state

    def run(self):
        debug_thread()

        if not download(self.state, self):
            return False

        return True
