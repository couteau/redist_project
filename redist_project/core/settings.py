# -*- coding: utf-8 -*-
"""QGIS Redistricting Project Plugin - Plugin Settings

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

from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.utils import iface


class RedistProjectSetttings:
    datapath: pathlib.Path
    iface: QgisInterface

    def __init__(self):
        self.datapath = pathlib.Path(
            QgsApplication.qgisSettingsDirPath()
        ) / "redist_data"
        self.iface = iface


settings = RedistProjectSetttings()
