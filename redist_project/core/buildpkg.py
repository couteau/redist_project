# -*- coding: utf-8 -*-
"""QGIS Redistricting Project Plugin - custom data package builder

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

from qgis.core import (
    QgsFeedback,
    QgsTask
)
from redistricting.core.Tasks._debug import debug_thread

from ..datapkg.cvap import add_cvap_data_to_gpkg
from ..datapkg.pl import process_pl
from ..datapkg.vr import add_vr_to_block
from .settings import settings
from .state import (
    State,
    geopackage_name
)
from .utils import tr


def build_geopackage(
    state: State,
    dec_year="2020",
    cvap_year=None,
    geogs=None,
    vr_path: pathlib.Path = None,
    feedback: QgsFeedback = None
):
    def progress(n):
        if feedback:
            feedback.setProgress(count + n * segment/total)

    gpkg_name = geopackage_name(state)
    gpkg_path = settings.datapath / gpkg_name

    if geogs is None:
        geogs = ['b', 'bg', 't', 'c', 'vtd', 'p', 'cousub', 'aiannh', 'city']

    total = 45
    if cvap_year:
        total += 45
    if vr_path and vr_path.exists():
        total += 10
    count = 0
    segment = 45
    process_pl(state.id, dec_year, geogs=geogs, gpkg=gpkg_path, progress=progress)
    count += segment
    if cvap_year:
        segment = 45
        add_cvap_data_to_gpkg(gpkg_path, state.id, dec_year, cvap_year, prog_cb=progress)
        count += segment

    if vr_path and vr_path.exists():
        segment = 10
        add_vr_to_block(gpkg_path, dec_year, vr_path, progress=progress)
        count += segment

    feedback.setProgress(100)


class BuildGeopackageTask(QgsTask):
    def __init__(self, state: State, dec_year="2020", cvap_year=None, geogs=None, vr_path: pathlib.Path = None) -> None:
        super().__init__(tr("Build redistricting data package for %s") % state.name, QgsTask.AllFlags)
        self.state = state
        self.dec_year = dec_year
        self.acs_year = cvap_year
        self.geogs = geogs
        self.vr_path = vr_path

    def updateDescription(self, record):
        self.setDescription(record.getMessage())
        self.progressChanged.emit(self.progress())

    def run(self):
        debug_thread()
        logging.root.setLevel(logging.INFO)
        logging.root.addFilter(self.updateDescription)
        build_geopackage(self.state, self.dec_year, self.acs_year, self.geogs, self.vr_path, self)
        logging.root.removeFilter(self.updateDescription)

        return True
