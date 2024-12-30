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
from qgis.PyQt.QtCore import (
    QModelIndex,
    pyqtSignal
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QWizardPage
)

from ..core.getpkg import build_gpkg
from ..core.state import (
    State,
    StateList
)
from .DlgStateGpkg import AcquireStateGpkgDialog
from .models import (
    GeographyListModel,
    StateListModel,
    SubdivisionListModel
)
from .ui.WzpGeography import Ui_wzpGeography


class DlgNewProjectGeographyPage(Ui_wzpGeography, QWizardPage):
    stateChanged = pyqtSignal(State, name="stateChanged")

    def __init__(self, states: dict[str, StateList], parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.states = states
        self.cmDecennial.addItems(states.keys())
        self.cmDecennial.setCurrentIndex(self.cmDecennial.count() - 1)
        self.cmDecennial.currentTextChanged.connect(self.updateStateList)

        self.year = self.cmDecennial.currentText()
        self.state_model = StateListModel(self.states[self.year], self)
        self.geog_model = GeographyListModel(None, parent=self)
        self.subdiv_model = SubdivisionListModel(None, "", parent=self)
        self._state = None
        self.selected_geog = None
        self.selected_subdiv = None

        self.cmbState.setModel(self.state_model)
        self.cmbState.setModelColumn(1)
        self.cmbState.setCurrentIndex(-1)
        self.cmbState.currentIndexChanged.connect(self.cmbStateIndexChanged)

        self.cmbSubdivisionGeography.setModel(self.geog_model)
        self.cmbSubdivisionGeography.setModelColumn(1)
        self.cmbSubdivisionGeography.currentIndexChanged.connect(
            self.cmbSubdivisionGeographyIndexChanged
        )

        self.cmbSubdivisionName.setModel(self.subdiv_model)
        self.cmbSubdivisionName.setModelColumn(1)
        self.cmbSubdivisionName.currentIndexChanged.connect(
            self.cmbSubdivisionNameIndexChanged
        )
        self.btnCustomGpkg.clicked.connect(self.createCustomPackage)

    @property
    def state(self) -> State:
        return self._state

    @state.setter
    def state(self, value: State):
        self._state = value
        self.stateChanged.emit(self._state)

    def updateStateList(self, year):
        self.year = year
        self.state_model.state_list = self.states[year]
        # self.cmbState.setCurrentIndex(-1)

    def cmbStateIndexChanged(self, index):
        self.cmbSubdivisionGeography.clear()
        self.cmbSubdivisionName.clear()
        self.cmbSubdivisionGeography.setEnabled(False)
        self.cmbSubdivisionName.setEnabled(False)
        if index == -1:
            self.geog_model.state = None
            self.subdiv_model.state = None
            self.subdiv_model.geog = None
            self.state = None
            self.selected_geog = None
            self.selected_subdiv = None
            self.btnCustomGpkg.setEnabled(False)
        else:
            self.state = self.states[self.year][index]

            self.gbxSubdivision.setEnabled(True)
            self.rbEntireState.setChecked(True)

            self.geog_model.state = self._state
            self.cmbSubdivisionGeography.setCurrentIndex(-1)
            self.selected_geog = None

            self.subdiv_model.state = self._state
            self.subdiv_model.geog = None
            self.cmbSubdivisionName.setCurrentIndex(-1)
            self.selected_subdiv = None
            self.btnCustomGpkg.setEnabled(True)

    def cmbSubdivisionGeographyIndexChanged(self, index: int):
        if index == -1:
            self.subdiv_model.geog = None
            self.selected_geog = None
            self.selected_subdiv = None
        else:
            self.selected_geog = self.geog_model.geographies[index]
            self.subdiv_model.geog = self.selected_geog.geog
            self.cmbSubdivisionName.setCurrentIndex(-1)
            self.selected_subdiv = None

    def cmbSubdivisionNameIndexChanged(self, index: int):
        self.selected_subdiv = self.subdiv_model.subdivisions[index]

    def validatePage(self) -> bool:
        if self._state is None:
            return False

        if not self._state.gpkg_exists():
            return False

        if self.rbSubdivision.isChecked():
            return self.selected_geog is not None and self.selected_subdiv is not None

        return True

    def createCustomPackage(self):
        def addCustomPackage():
            self.state = state

            self.states[state.year].add_custom_package(state)
            index = self.states[state.year].index(state)
            self.state_model.beginInsertRows(QModelIndex(), index, index)
            self.state_model.endInsertRows()
            self.cmbState.setCurrentIndex(index)

        state = State.fromState(self.state)
        dlg = AcquireStateGpkgDialog(state, True, parent=self.wizard())
        if dlg.exec() == QDialog.Accepted:
            state.package_name = dlg.edPackageName.text()

            build_gpkg(
                state,
                dlg.cmDecennialYear.currentText(),
                dlg.cmCVAPYear.currentText(),
                dlg.fwL2VRData.filePath(),
                dlg.addlEquivalencies,
                dlg.addlShapefiles,
                addCustomPackage,
                self.wizard()
            )
