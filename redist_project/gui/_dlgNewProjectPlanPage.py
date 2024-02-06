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
from qgis.PyQt.QtWidgets import QWizardPage

from ..core.state import State
from .ui.WzpPlanParameters import Ui_wzpPlanParameters


class DlgNewProjectPlanPage(Ui_wzpPlanParameters, QWizardPage):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.state = None
        self.registerField("include-vap", self.cbIncludeVAP)
        self.registerField("include-cvap", self.cbIncludeCVAP)
        self.registerField("include-vr", self.cbIncludeReg)
        self.registerField("numdistricts", self.sbxNumDistricts)
        self.registerField("numseats", self.sbxNumSeats)
        self.registerField("deviation", self.sbxMaxDeviation, 'value', self.sbxMaxDeviation.valueChanged)

        self.sbxNumDistricts.valueChanged.connect(self.numDistrictsChanged)
        self.sbxNumSeats.valueChanged.connect(self.numSeatsChanged)
        self.linkSeats = True

    def initializePage(self):
        super().initializePage()
        state: State = self.wizard().state
        if self.state != state:
            self.state = state
            if state:
                self.cbIncludeVAP.setChecked(True)
                cvap = state.has_cvap()
                self.cbIncludeCVAP.setEnabled(cvap)
                if not cvap:
                    self.cbIncludeCVAP.setChecked(False)
                vr = state.has_vr()
                self.cbIncludeReg.setEnabled(vr)
                if not vr:
                    self.cbIncludeReg.setChecked(False)

    def numDistrictsChanged(self, value: int):
        self.sbxNumSeats.setMinimum(value)
        if self.linkSeats or self.field('numseats') < value:
            self.sbxNumSeats.setValue(value)
            self.linkSeats = True
        self.completeChanged.emit()

    def numSeatsChanged(self, value: int):
        if value < self.field('numdistricts'):
            self.sbxNumSeats.setValue(self.field('numdistricts'))
        else:
            self.linkSeats = value == self.field('numdistricts')

    def isComplete(self) -> bool:
        complete = super().isComplete()
        return complete and self.field('numdistricts') > 1
