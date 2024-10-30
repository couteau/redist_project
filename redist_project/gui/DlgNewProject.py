# -*- coding: utf-8 -*-
"""QGIS Redistricting Project Plugin - New Project Dialog

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
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QWizard

from ..core.basemaps import BASEMAP_INDEX
from ..core.state import (
    State,
    StateList
)
from ..datapkg.geography import geographies
from ._dlgNewProjectFieldsPage import DlgNewProjectFieldsPage
from ._dlgNewProjectGeographyPage import DlgNewProjectGeographyPage
from ._dlgNewProjectInclGeogPage import DlgNewProjectIncludeGeographyPage
from ._dlgNewProjectPlanPage import DlgNewProjectPlanPage


class NewProjectDialog(QWizard):
    stateChanged = pyqtSignal(State, name="stateChanged")

    @property
    def state(self) -> State:
        return self.geog_page.state

    @state.setter
    def state(self, value: State):
        self.geog_page.state = value

    def __init__(self, states: dict[str, StateList], parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr('New Redistricting Project'))
        self.wizardStyle = QWizard.ModernStyle
        self.setOptions(QWizard.NoBackButtonOnStartPage |
                        QWizard.CancelButtonOnLeft |
                        QWizard.NoDefaultButton |
                        QWizard.HaveFinishButtonOnEarlyPages |
                        QWizard.HaveHelpButton |
                        QWizard.HelpButtonOnRight)

        self.geog_page = DlgNewProjectGeographyPage(states, self)
        self.geog_page.stateChanged.connect(self.stateChanged)

        self.addPage(self.geog_page)

        self.incl_geog_page = DlgNewProjectIncludeGeographyPage(self)
        self.addPage(self.incl_geog_page)

        self.addPage(DlgNewProjectPlanPage(self))

        self.fields_page = DlgNewProjectFieldsPage(self)
        self.addPage(self.fields_page)

    @property
    def subdivision_geog(self):
        if self.geog_page.selected_subdiv:
            return self.geog_page.selected_subdiv.geog.name
        return None

    @property
    def subdivision_geoid(self):
        if self.geog_page.selected_subdiv:
            return self.geog_page.selected_subdiv.geoid
        return None

    @property
    def geographies(self):
        return {"b": geographies["b"]} | {
            g: geog
            for g, geog in self.state.get_geographies().items()  # pylint: disable=no-member
            if geog.name in self.incl_geog_page.get_selected_geogs()
        }

    @property
    def includeVAP(self):
        return self.field("include-vap")

    @property
    def includeCVAP(self):
        return self.field("include-cvap")

    @property
    def includeVR(self):
        return self.field("include-vr")

    @property
    def numDistricts(self):
        return self.field("numdistricts")

    @property
    def numSeats(self):
        return self.field("numseats")

    @property
    def deviation(self):
        return self.field("deviation") / 100

    @property
    def dataFields(self):
        return self.fields_page.fields

    @property
    def includeBaseMap(self):
        return self.incl_geog_page.cbBaseMap.isChecked()

    @property
    def baseMap(self):
        return self.incl_geog_page.cmbBaseMap.currentData(BASEMAP_INDEX) \
            if self.incl_geog_page.cbBaseMap.isChecked() else None

    @property
    def includeCustomLayers(self) -> bool:
        return self.incl_geog_page.cbCustomLayers.isChecked() \
            and self.incl_geog_page.cmbBaseMap.currentData(BASEMAP_INDEX)[0] is not None
