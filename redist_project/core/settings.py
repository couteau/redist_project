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

from qgis.core import (
    QgsApplication,
    QgsSettings
)
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
        self.settings = QgsSettings()
        self._customPackages = None

    @property
    def customPackages(self):
        if self._customPackages is None:
            self._customPackages = []
            self.settings.beginGroup("redistricting", section=QgsSettings.Section.Plugins)
            c = self.settings.beginReadArray("custom-packages")
            for i in range(c):
                self.settings.setArrayIndex(i)
                st = self.settings.value("state")
                custom_id = self.settings.value("id")
                name = self.settings.value("name")
                yr = self.settings.value("year")
                gpkg = self.settings.value("gpkg-path")
                self._customPackages.append({"st": st, "id": custom_id, "dec_year": yr,
                                            "gpkg_path": gpkg, "name": name})
            self.settings.endArray()
            self.settings.endGroup()

        return self._customPackages

    def saveCustomPackages(self):
        # self.settings.beginGroup("redistricting", section=QgsSettings.Section.Plugins)
        # self.settings.beginWriteArray("custom-packages", len(self.customPackages))
        # for i, p in enumerate(self.customPackages):
        #     self.settings.setArrayIndex(i)
        #     self.settings.setValue("state", p["st"])
        #     self.settings.setValue("id", p["id"])
        #     self.settings.setValue("name", p["name"])
        #     self.settings.setValue("year", p["dec_year"])
        #     self.settings.setValue("gpkg-path", p["gpkg_path"])
        # self.settings.endArray()
        # self.settings.endGroup()
        pass

    def addCustomPackage(self, st, custom_id: str, year, name, gpkg_path):
        self.customPackages.append({"st": st, "id": custom_id, "dec_year": year, "gpkg_path": gpkg_path, "name": name})
        self.saveCustomPackages()


settings = RedistProjectSetttings()
