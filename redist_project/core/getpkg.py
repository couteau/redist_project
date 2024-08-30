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
import logging
import pathlib
from typing import (
    Callable,
    Optional,
    Union
)

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QProgressDialog,
    QWidget
)
from qgis.utils import iface

from ..intl import tr
from .buildpkg import BuildGeopackageTask
from .download import StateDownloadTask
from .state import State


def download_gpkg(state: State, parent: QWidget = None):
    msg = tr("Downloading redistricting data for %s") % state.name

    dlg = QProgressDialog(
        msg, tr('Cancel'),
        0, 100,
        parent,
        Qt.WindowStaysOnTopHint
    )
    dlg.setAttribute(Qt.WA_DeleteOnClose, True)
    if parent != iface.mainWindow():
        dlg.setWindowModality(Qt.WindowModal)

    task = StateDownloadTask(state)
    dlg.canceled.connect(task.cancel)
    task.progressChanged.connect(lambda p: dlg.setValue(round(p)))
    task.taskTerminated.connect(dlg.close)
    task.taskCompleted.connect(dlg.close)
    QgsApplication.taskManager().addTask(task)


def build_gpkg(
    state: State,
    dec_year: str,
    cvap_year: str,
    vr_path: Union[str, pathlib.Path],
    addl_bef: list,
    addl_shp: list,
    on_created: Optional[Callable] = None,  # pylint: disable=deprecated-typing-alias
    parent: QWidget = None
):
    def update_progress(p):
        dlg.setValue(round(p))
        text = task.description()
        if len(text) > 49:
            text = text[:23] + "..." + text[-23:]
        dlg.setLabelText(text)

    msg = tr("Building redistricting data package for %s") % state.name

    dlg = QProgressDialog(
        msg, tr('Cancel'),
        0, 100,
        parent,
        Qt.Dialog | Qt.WindowStaysOnTopHint
    )
    dlg.setWindowTitle(tr("Build Redistricting Package"))
    dlg.setAttribute(Qt.WA_DeleteOnClose, True)
    if parent != iface.mainWindow():
        dlg.setWindowModality(Qt.WindowModal)

    if isinstance(vr_path, str) and vr_path != "":
        vr_path = pathlib.Path(vr_path)

    task = BuildGeopackageTask(state, dec_year, cvap_year, None, vr_path, addl_bef, addl_shp)
    dlg.canceled.connect(task.cancel)

    task.progressChanged.connect(update_progress)
    task.taskTerminated.connect(dlg.close)
    task.taskCompleted.connect(dlg.close)
    if on_created is not None:
        task.taskCompleted.connect(on_created)
    logging.root.setLevel(logging.INFO)
    QgsApplication.taskManager().addTask(task)
    return task
