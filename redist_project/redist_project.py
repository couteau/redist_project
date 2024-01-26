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
from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import (
    QCoreApplication,
    Qt
)
from qgis.PyQt.QtWidgets import (
    QAction,
    QDialog,
    QProgressDialog
)

from .core.state import StateList
from .gui.DlgNewProject import NewProjectDialog
from .pkg_utils.download import StateDownloadTask


class RdProjectGenerator:
    """QGIS Redistricting Plugin"""

    def __init__(self, iface: QgisInterface):
        self.name = self.__class__.__name__
        self.iface = iface

        self.newProjectAction = None
        self.states = StateList("2020")

    @staticmethod
    def tr(message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('redistricting', message)

    def initGui(self):
        """Create the menu entries, toolbar buttons, actions, and dock widgets."""
        self.newProjectAction = QAction(
            self.iface.mainWindow()
        )
        self.newProjectAction.setIcon(
            QgsApplication.getThemeIcon('/mActionFileNew.svg'))
        self.newProjectAction.setText(self.tr("New Districting Project"))
        self.newProjectAction.setToolTip(
            self.tr("Create a new redistricting project"))
        self.newProjectAction.triggered.connect(self.newProject)

        menu = self.iface.projectMenu()
        menu.insertAction(menu.actions()[1], self.newProjectAction)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

    def newProject(self):
        dlg = NewProjectDialog(self.states, self.iface.mainWindow())
        if dlg.exec_() == QDialog.Accepted:
            pass

    def download_gpkg(self, state: str):
        msg = f"Downloading redistricting data for {self.states[state].name}"
        dlg = QProgressDialog(
            msg, self.tr('Cancel'),
            0, 100,
            self.iface.mainWindow(),
            Qt.WindowStaysOnTopHint
        )
        dlg.setAttribute(Qt.WA_DeleteOnClose, True)

        task = self.states[state].download_gpkg(False)
        dlg.canceled.connect(task.cancel)
        task.taskTerminated.connect(dlg.close)
        task.taskCompleted.connect(dlg.close)
        QgsApplication.taskManager().addTask(task)
