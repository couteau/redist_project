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
from typing import Any

from qgis.core import (
    QgsFeedback,
    QgsTask
)
from redistricting.exception import CanceledError
from redistricting.services.Tasks._debug import debug_thread

from ..datapkg.bef import (
    BEFData,
    add_bef_to_block
)
from ..datapkg.cvap import add_cvap_data_to_gpkg
from ..datapkg.pl import process_pl
from ..datapkg.shp import import_shape
from ..datapkg.vr import add_vr_to_block
from .settings import settings
from .state import State
from .utils import tr


def build_geopackage(
    state: State,
    dec_year="2020",
    cvap_year=None,
    geogs=None,
    vr_path: pathlib.Path = None,
    addl_bef: list[BEFData] = None,
    addl_shp: dict[str, str] = None,
    feedback: QgsFeedback = None
):
    def progress(n):
        if feedback:
            if feedback.isCanceled():
                raise CanceledError()

            feedback.setProgress(count + n * segment/total)

    src_path = settings.datapath / "cache"
    if not src_path.exists():
        src_path.mkdir(parents=True)

    gpkg_name = state.gpkg
    gpkg_path = settings.datapath / gpkg_name

    if geogs is None:
        geogs = ['b', 'bg', 't', 'c', 'vtd', 'p', 'cousub', 'aiannh', 'city']

    total = 45
    if cvap_year:
        total += 45
    if vr_path and vr_path.exists():
        total += 10

    if addl_bef:
        total += 10 * len(addl_bef)

    if addl_shp:
        total += 10 * len(addl_shp)

    count = 0
    segment = 45
    if not process_pl(
        state.code,
        dec_year,
        geogs=geogs,
        gpkg=gpkg_path,
        src_path=src_path,
        progress=progress
    ) or feedback.isCanceled():
        return False

    count += segment
    if cvap_year:
        segment = 45
        if not add_cvap_data_to_gpkg(
            gpkg_path,
            state.code,
            dec_year,
            cvap_year,
            src_path=src_path,
            prog_cb=progress
        ) or feedback.isCanceled():
            return False
        count += segment

    if vr_path and vr_path.exists():
        segment = 10
        add_vr_to_block(gpkg_path, dec_year, vr_path, progress=progress)
        count += segment

    if addl_bef:
        segment = 10
        for bef in addl_bef:
            add_bef_to_block(gpkg_path, dec_year, bef, progress=progress)
            count += segment

    if addl_shp:
        segment = 10
        for lyr, shp in addl_shp.items():
            import_shape(gpkg_path, shp, lyr, progress=progress)
            count += segment

    feedback.setProgress(100)


class BuildGeopackageTask(QgsTask):
    def __init__(
        self,
        state: State,
        dec_year="2020",
        cvap_year=None,
        geogs=None,
        vr_path: pathlib.Path = None,
        addl_bef: list[dict[str, Any]] = None,
        addl_shp: dict[str, str] = None
    ):
        super().__init__(tr("Build redistricting data package for %s") % state.name, QgsTask.AllFlags)
        self.state = state
        self.dec_year = dec_year
        self.acs_year = cvap_year
        self.geogs = geogs
        self.vr_path = vr_path
        self.addl_bef = addl_bef
        self.addl_shp = addl_shp
        self.exception = None

    def updateDescription(self, record: logging.LogRecord):
        self.setDescription(record.getMessage())
        self.progressChanged.emit(self.progress())

    def run(self):
        debug_thread()
        logging.root.setLevel(logging.INFO)
        logging.root.addFilter(self.updateDescription)
        try:
            build_geopackage(self.state, self.dec_year, self.acs_year, self.geogs,
                             self.vr_path, self.addl_bef, self.addl_shp, self)
        except CanceledError:
            return False
        except Exception as e:  # pylint: disable=broad-except
            self.exception = e
            return False
        finally:
            logging.root.removeFilter(self.updateDescription)

        return True
