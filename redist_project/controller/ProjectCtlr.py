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
import json
from typing import (
    Callable,
    Optional
)

from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsReadWriteContext
)
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import plugins
from redistricting.controllers import PlanController
from redistricting.gui import DlgEditPlan
from redistricting.models import RedistrictingPlan
from redistricting.redistricting import Redistricting
from redistricting.services import (
    PlanBuilder,
    PlanEditor,
    PlanStylerService
)

from ..actions import RedistProjectActions
from ..core.buildproj import build_project
from ..core.getpkg import (
    build_gpkg,
    download_gpkg
)
from ..core.settings import settings
from ..core.state import (
    State,
    StateList
)
from ..gui import (
    AcquireStateGpkgDialog,
    NewPlanDialog,
    NewProjectDialog
)
from ..intl import tr


class ProjectController(QObject):

    def __init__(self, iface: QgisInterface, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.iface = iface
        self.actions = RedistProjectActions()
        self.project = QgsProject.instance()
        self.redist_plugin: Redistricting = None
        self.planController: PlanController = None
        self.planStyler: PlanStylerService = None
        self.patched = False

        self.states = {
            "2010": StateList("2010"),
            "2020": StateList("2020")
        }

        self.state: State = None
        self.year: str = None
        self.template: dict = None
        self.new_state: State = None

        self.newProjectAction = self.actions.createAction(
            "newProjectAction",
            QIcon(':/plugins/redist_project/newproj.svg'),
            tr("New Districting Project"),
            tr("Create a new redistricting project"),
            self.newProject,
            self
        )

        self.advancedNewPlan: Callable = None  # pylint: disable=deprecated-typing-alias
        self.advancedEditPlan: Callable = None  # pylint: disable=deprecated-typing-alias

        self.buildPackageAction = self.actions.createAction(
            "buildPackageAction",
            QgsApplication.getThemeIcon('/mNewFeature'),
            tr("State Package"),
            tr("Download state redistricting data package"),
            self.acquireStatePackage,
            self
        )

        self.customPackageAction = self.actions.createAction(
            "customPackageAction",
            QgsApplication.getThemeIcon('/mNewFeature'),
            tr("Create Package"),
            tr("Create a custom state redistricting data package"),
            self.createCustomPackage,
            self
        )

    def readProjectParams(self):
        state, success = self.project.readEntry('redistricting', 'us-state', None)
        if success and state:
            year, success = self.project.readEntry('redistricting', 'us-decennial', None)
            if success and year:
                s, success = self.project.readEntry('redistricting', 'us-template')
            else:
                success = False

            if success and s:
                self.state = self.states[year][state]
                self.year = year
                self.template = RedistrictingPlan.deserialize(json.loads(s), self.project)
            else:
                success = False
        else:
            success = False

        if success:
            self.patchRedistrictingMenu(True)
        else:
            self.patchRedistrictingMenu(False)

    def load(self):
        self.redist_plugin: Redistricting = plugins["redistricting"]
        self.planController = self.redist_plugin.planController
        self.planStyler = self.redist_plugin.planStyler

        self.advancedEditPlan = self.planController.editPlan
        self.advancedNewPlan = self.planController.newPlan

        self.project.readProjectWithContext.connect(self.onReadProject)
        self.project.cleared.connect(self.onCloseProject)

        self.patched = None

    def unload(self):
        self.patchRedistrictingMenu(False)

        self.project.readProjectWithContext.disconnect(self.onReadProject)
        self.project.cleared.disconnect(self.onCloseProject)

    def onReadProject(self, doc: QDomDocument, context: QgsReadWriteContext):  # pylint: disable=unused-argument
        self.readProjectParams()

    def onCloseProject(self):
        self.state = None
        self.year = None
        self.template = None
        self.patchRedistrictingMenu(False)

    def patchRedistrictingMenu(self, patch: bool = True):
        if self.redist_plugin:
            if patch and not self.patched:
                self.redist_plugin.planController.actionNewPlan.triggered.disconnect(self.advancedNewPlan)
                self.redist_plugin.planController.actionEditPlan.triggeredForPlan.disconnect(self.advancedEditPlan)
                self.redist_plugin.planController.actionNewPlan.triggered.connect(self.newPlan)
                self.redist_plugin.planController.actionEditPlan.triggeredForPlan.connect(self.editPlan)
            elif not patch and self.patched:
                self.redist_plugin.planController.actionNewPlan.triggered.disconnect(self.newPlan)
                self.redist_plugin.planController.actionEditPlan.triggeredForPlan.disconnect(self.editPlan)
                self.redist_plugin.planController.actionNewPlan.triggered.connect(self.advancedNewPlan)
                self.redist_plugin.planController.actionEditPlan.triggeredForPlan.connect(self.advancedEditPlan)

    def newProject(self):
        dlg = NewProjectDialog(self.states, self.iface.mainWindow())
        dlg.stateChanged.connect(self.stateChanged)

        if dlg.exec() == QDialog.Accepted:
            if self.iface.newProject(True):
                build_project(
                    dlg.state,
                    numdistricts=dlg.numDistricts,
                    numseats=dlg.numSeats,
                    deviation=dlg.deviation,
                    include_vap=dlg.includeVAP,
                    include_cvap=dlg.includeCVAP,
                    include_vr=dlg.includeVR,
                    geogs=dlg.geographies,
                    subdiv_geog=dlg.subdivision_geog,
                    subdiv_id=dlg.subdivision_geoid,
                    fields=dlg.dataFields,
                    base_map=dlg.baseMap,
                    custom_layers=dlg.customLayers
                )
                self.readProjectParams()

    def showCreatePackageDialog(
        self,
        state: State,
        custom: bool = False,
        on_created: Optional[Callable] = None  # pylint: disable=deprecated-typing-alias
    ):
        dlg = AcquireStateGpkgDialog(state, custom, parent=self.iface.mainWindow())
        if dlg.exec() == QDialog.Accepted:
            if dlg.rbStandardPackage.isChecked():
                download_gpkg(state, self.newProjectDlg)
            else:
                if custom:
                    state.custom_name = dlg.edPackageName.text()

                build_gpkg(
                    state,
                    dlg.cmDecennialYear.currentText(),
                    dlg.cmCVAPYear.currentText(),
                    dlg.fwL2VRData.filePath(),
                    dlg.addlEquivalencies,
                    dlg.addlShapefiles,
                    on_created,
                    self.iface.mainWindow()
                )
            return True

        return False

    def acquireStatePackage(self):
        self.showCreatePackageDialog(self.new_state)

    def createCustomPackage(self):
        def addCustomPackage():
            self.new_state = state
            self.states[state.year].add_custom_package(state)
            settings.addCustomPackage(
                state.st.state,
                state.id,
                state.year,
                state.custom_name,
                str(state.gpkg)
            )

        state = State.fromState(self.new_state)
        self.showCreatePackageDialog(state, True, on_created=addCustomPackage)

    def stateChanged(self, state: Optional[State]):
        self.new_state = state
        if state is None:
            return

        if not state.gpkg_exists():
            self.acquireStatePackage()

    def newPlan(self):
        dlg = NewPlanDialog(self.state, self.template, self.iface.mainWindow())
        r = dlg.exec()
        if r == QDialog.Accepted:
            builder = PlanBuilder.fromPlan(self.template)
            builder.setName(dlg.planName) \
                .setNumDistricts(dlg.numDistricts) \
                .setNumSeats(dlg.numSeats) \
                .setDescription(dlg.description) \
                .setDataFields(dlg.dataFields) \
                .setGeoPackagePath(dlg.gpkgPath)

            self.planController.buildPlan(builder)
        elif r == 2:  # advanced button clicked - show default new plan dialog
            plan = PlanBuilder.fromPlan(self.template) \
                .setName(dlg.planName) \
                .setDescription(dlg.description) \
                .setNumDistricts(dlg.numDistricts) \
                .setNumSeats(dlg.numSeats) \
                .setDataFields(dlg.dataFields) \
                .setGeoPackagePath(dlg.gpkgPath) \
                .createPlan(self.project, False)
            dlgNewPlan = DlgEditPlan(plan, self.iface.mainWindow())
            dlgNewPlan.setWindowTitle(self.tr('New Redistricting Plan'))
            if dlgNewPlan.exec_() == QDialog.Accepted:
                builder = PlanBuilder() \
                    .setName(dlgNewPlan.planName()) \
                    .setNumDistricts(dlgNewPlan.numDistricts()) \
                    .setNumSeats(dlgNewPlan.numSeats()) \
                    .setDescription(dlgNewPlan.description()) \
                    .setDeviation(dlgNewPlan.deviation()) \
                    .setGeoIdField(dlgNewPlan.geoIdField()) \
                    .setGeoDisplay(dlgNewPlan.geoIdCaption()) \
                    .setGeoLayer(dlgNewPlan.geoLayer()) \
                    .setPopLayer(dlgNewPlan.popLayer()) \
                    .setJoinField(dlgNewPlan.joinField()) \
                    .setPopField(dlgNewPlan.popField()) \
                    .setPopFields(dlgNewPlan.popFields()) \
                    .setDataFields(dlgNewPlan.dataFields()) \
                    .setGeoFields(dlgNewPlan.geoFields()) \
                    .setGeoPackagePath(dlgNewPlan.gpkgPath())

                self.planController.buildPlan(builder)

    def editPlan(self, plan):
        dlg = NewPlanDialog(plan, self.iface.mainWindow())
        dlg.setWindowTitle(self.tr('Edit Redistricting Plan'))
        r = dlg.exec()
        if r == QDialog.Accepted:
            builder = PlanEditor.fromPlan(plan)
            builder.setName(dlg.planName) \
                .setNumDistricts(dlg.numDistricts) \
                .setNumSeats(dlg.numSeats) \
                .setDescription(dlg.description) \
                .setDataFields(dlg.dataFields)
            if builder.updatePlan():
                self.project.setDirty()
                if 'num-districts' in builder.modifiedFields:
                    self.redist_plugin.planStyler.stylePlan(plan)
        elif r == 2:  # advanced button clicked - show default new plan dialog
            dlgEditPlan = DlgEditPlan(plan, self.iface.mainWindow())
            dlgEditPlan.setWindowTitle(self.tr('Edit Redistricting Plan'))
            if dlgEditPlan.exec() == QDialog.Accepted:
                builder = PlanEditor.fromPlan(plan) \
                    .setName(dlgEditPlan.planName()) \
                    .setNumDistricts(dlgEditPlan.numDistricts()) \
                    .setNumSeats(dlgEditPlan.numSeats()) \
                    .setDescription(dlgEditPlan.description()) \
                    .setDeviation(dlgEditPlan.deviation()) \
                    .setGeoDisplay(dlgEditPlan.geoIdCaption()) \
                    .setPopLayer(dlgEditPlan.popLayer()) \
                    .setPopField(dlgEditPlan.popField()) \
                    .setPopFields(dlgEditPlan.popFields()) \
                    .setDataFields(dlgEditPlan.dataFields()) \
                    .setGeoFields(dlgEditPlan.geoFields())

                if builder.updatePlan():
                    self.project.setDirty()
                    if 'num-districts' in builder.modifiedFields:
                        self.planStyler.stylePlan(plan)
