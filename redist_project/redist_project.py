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
import logging
import pathlib
from copy import deepcopy
from typing import Optional

from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsReadWriteContext
)
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import (
    QCoreApplication,
    Qt
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QAction,
    QDialog,
    QProgressDialog,
    QWidget
)
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import (
    plugins,
    unloadPlugin
)
from redistricting.core import (
    PlanBuilder,
    RedistrictingPlan
)
from redistricting.gui import DlgEditPlan
from redistricting.redistricting import Redistricting

from .core.buildpkg import BuildGeopackageTask
from .core.buildproj import build_project
from .core.download import StateDownloadTask
from .core.state import (
    State,
    StateList
)
from .gui.DlgNewPlan import NewPlanDialog
from .gui.DlgNewProject import NewProjectDialog
from .gui.DlgStateGpkg import DlgStateGpkg
from .resources import *  # pylint: disable=wildcard-import,unused-wildcard-import


class RdProjectGenerator:
    """QGIS Redistricting Plugin"""

    def __init__(self, iface: QgisInterface):
        self.name = self.__class__.__name__
        self.iface = iface
        self.project = QgsProject.instance()
        self.redist_plugin = None

        self.newPlanOrig = None
        self.newProjectAction = None
        self.newProjectDlg = None
        self.states = {
            "2010": StateList("2010"),
            "2020": StateList("2020")
        }

        self.state = None
        self.year = None
        self.template = None

    @staticmethod
    def tr(message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('redistricting', message)

    def initGui(self):
        """Create the menu entries, toolbar buttons, actions, and dock widgets."""
        self.redist_plugin: Redistricting = plugins["redistricting"]

        self.project.readProjectWithContext.connect(self.onReadProject)
        self.project.cleared.connect(self.onCloseProject)

        self.newProjectAction = QAction(
            self.iface.mainWindow()
        )
        self.newProjectAction.setIcon(
            QIcon(':/plugins/redist_project/newproj.svg')
        )
        self.newProjectAction.setText(self.tr("New Districting Project"))
        self.newProjectAction.setToolTip(
            self.tr("Create a new redistricting project")
        )
        self.newProjectAction.triggered.connect(self.newProject)

        menu = self.iface.projectMenu()
        menu.insertAction(menu.actions()[1], self.newProjectAction)

        toolbar = self.iface.fileToolBar()
        toolbar.insertAction(toolbar.actions()[1], self.newProjectAction)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        toolbar = self.iface.fileToolBar()
        toolbar.removeAction(self.newProjectAction)

        menu = self.iface.projectMenu()
        menu.removeAction(self.newProjectAction)

        self.project.readProjectWithContext.disconnect(self.onReadProject)

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

    def onReadProject(self, doc: QDomDocument, context: QgsReadWriteContext):  # pylint: disable=unused-argument
        self.readProjectParams()

    def onCloseProject(self):
        self.state = None
        self.year = None
        self.template = None

    def patchRedistrictingMenu(self, patch: bool = True):
        if self.redist_plugin:
            if patch and self.newPlanOrig is None:
                self.newPlanOrig = self.redist_plugin.newPlan
                self.redist_plugin.actionNewPlan.triggered.disconnect(self.redist_plugin.newPlan)
                self.redist_plugin.actionNewPlan.triggered.connect(self.newPlan)
            elif not patch and self.newPlanOrig is not None:
                self.redist_plugin.actionNewPlan.triggered.disconnect(self.newPlan)
                self.redist_plugin.actionNewPlan.triggered.connect(self.redist_plugin.newPlan)
                self.newPlanOrig = None
        else:
            unloadPlugin(self.name)

    def newPlan(self):
        # if self.project.isDirty():
        #     # the project must be saved before a plan can be created
        #     self.iface.messageBar().pushMessage(
        #         self.tr("Wait!"),
        #         self.tr("Please save your project before "
        #                 "creating a redistricting plan."),
        #         level=Qgis.MessageLevel.Warning,
        #         duration=5
        #     )
        #     return

        plan = deepcopy(self.template)
        dlg = NewPlanDialog(self.state, plan, self.iface.mainWindow())
        r = dlg.exec_()
        if r == QDialog.Accepted:
            builder = PlanBuilder.fromPlan(plan)
            builder.setName(dlg.planName) \
                .setNumDistricts(dlg.numDistricts) \
                .setNumSeats(dlg.numSeats) \
                .setDescription(dlg.description) \
                .setDataFields(dlg.dataFields) \
                .setGeoPackagePath(dlg.gpkgPath)

            self.redist_plugin.buildPlan(builder)
        elif r == 2:  # advanced button clicked - show default new plan dialog
            plan = PlanBuilder.fromPlan(plan) \
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

                self.redist_plugin.buildPlan(builder)

    def newProject(self):
        self.newProjectDlg = NewProjectDialog(self.states, self.iface.mainWindow())
        self.newProjectDlg.stateChanged.connect(self.stateChanged)
        if self.newProjectDlg.exec_() == QDialog.Accepted:
            if self.iface.newProject(True):
                build_project(
                    self.newProjectDlg.state,
                    numdistricts=self.newProjectDlg.numDistricts,
                    numseats=self.newProjectDlg.numSeats,
                    deviation=self.newProjectDlg.deviation,
                    include_vap=self.newProjectDlg.includeVAP,
                    include_cvap=self.newProjectDlg.includeCVAP,
                    include_vr=self.newProjectDlg.includeVR,
                    geogs=self.newProjectDlg.geographies,
                    subdiv_geog=self.newProjectDlg.subdivision_geog,
                    subdiv_id=self.newProjectDlg.subdivision_geoid,
                    fields=self.newProjectDlg.dataFields,
                    base_map=self.newProjectDlg.baseMap
                )
                self.readProjectParams()

        self.newProjectDlg = None

    def showPackageDlg(self, state: State):
        dlg = DlgStateGpkg(state, self.iface.mainWindow())
        if dlg.exec_() == QDialog.Accepted:
            if dlg.rbStandardPackage.isChecked():
                self.download_gpkg(state, self.newProjectDlg)
            else:
                self.build_gpkg(
                    state,
                    dlg.cmDecennialYear.currentText(),
                    dlg.cmCVAPYear.currentText(),
                    dlg.fwL2VRData.filePath(),
                    self.newProjectDlg
                )
            return True

        return False

    def download_gpkg(self, state: State, parent: QWidget = None):
        msg = self.tr("Downloading redistricting data for %s") % state.name
        if parent is None:
            parent = self.iface.mainWindow()

        dlg = QProgressDialog(
            msg, self.tr('Cancel'),
            0, 100,
            self.iface.mainWindow(),
            Qt.WindowStaysOnTopHint
        )
        dlg.setAttribute(Qt.WA_DeleteOnClose, True)
        if parent != self.iface.mainWindow():
            dlg.setWindowModality(Qt.WindowModal)

        task = StateDownloadTask(self)
        dlg.canceled.connect(task.cancel)
        task.progressChanged.connect(lambda p: dlg.setValue(round(p)))
        task.taskTerminated.connect(dlg.close)
        task.taskCompleted.connect(dlg.close)
        QgsApplication.taskManager().addTask(task)

    def build_gpkg(self, state: State, dec_year, cvap_year, vr_path, parent: QWidget = None):
        def update_progress(p):
            dlg.setValue(round(p))
            text = task.description()
            if len(text) > 49:
                text = text[:23] + "..." + text[-23:]
            dlg.setLabelText(text)
        msg = self.tr("Building redistricting data package for %s") % state.name
        if parent is None:
            parent = self.iface.mainWindow()

        dlg = QProgressDialog(
            msg, self.tr('Cancel'),
            0, 100,
            parent,
            Qt.Dialog | Qt.WindowStaysOnTopHint
        )
        dlg.setWindowTitle(self.tr("Build Redistricting Package"))
        dlg.setAttribute(Qt.WA_DeleteOnClose, True)
        if parent != self.iface.mainWindow():
            dlg.setWindowModality(Qt.WindowModal)

        task = BuildGeopackageTask(state, dec_year, cvap_year, None, pathlib.Path(vr_path))
        dlg.canceled.connect(task.cancel)

        task.progressChanged.connect(update_progress)
        task.taskTerminated.connect(dlg.close)
        task.taskCompleted.connect(dlg.close)
        logging.root.setLevel(logging.INFO)
        QgsApplication.taskManager().addTask(task)

    def stateChanged(self, state: Optional[State]):
        if state is None:
            return

        if not state.gpkg_exists():
            self.showPackageDlg(state)
