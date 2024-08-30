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
from qgis.core import QgsProject
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication
from qgis.utils import (
    plugins,
    unloadPlugin
)

from .actions import RedistProjectActions
from .controller.ProjectCtlr import ProjectController
from .resources import *  # pylint: disable=wildcard-import,unused-wildcard-import


class RdProjectGenerator:
    """QGIS Redistricting Plugin"""

    def __init__(self, iface: QgisInterface):
        self.name = self.__class__.__name__
        self.iface = iface
        self.project = QgsProject.instance()
        self.actions = RedistProjectActions(self.iface.mainWindow())
        self.projectController = ProjectController(self.iface, self.iface.mainWindow())
        self.redist_plugin = None

        self.newPlanOrig = None
        self.editPlanOrig = None
        self.newProjectDlg = None

    @staticmethod
    def tr(message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('redistricting', message)

    def initGui(self):
        """Create the menu entries, toolbar buttons, actions, and dock widgets."""
        if "redistricting" not in plugins:
            unloadPlugin(self.name)
            return

        self.projectController.load()

        menu = self.iface.projectMenu()
        menu.insertAction(menu.actions()[1], self.projectController.newProjectAction)

        toolbar = self.iface.fileToolBar()
        toolbar.insertAction(toolbar.actions()[1], self.projectController.newProjectAction)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        toolbar = self.iface.fileToolBar()
        toolbar.removeAction(self.projectController.newProjectAction)

        menu = self.iface.projectMenu()
        menu.removeAction(self.projectController.newProjectAction)

        self.projectController.unload()
