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
from typing import Optional

from qgis.PyQt.QtWidgets import (
    QWidget,
    QWizardPage
)

from ..core.state import State
from .ui.WzpInclGeogs import Ui_wzpIncludeGeography


class DlgNewProjectIncludeGeographyPage(Ui_wzpIncludeGeography, QWizardPage):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUi(self)
        self.geogWidgets = (self.cbAIANNH, self.cbBlkGrp, self.cbConcity, self. cbCounty,
                            self.cbCousub, self.cbPlace, self.cbTract, self.cbVTD)

    def initializePage(self):
        super().initializePage()
        state: State = self.wizard().state

        geogs = {g.name for g in state.get_geographies().values()}

        for w in self.geogWidgets:
            w.setEnabled(w.objectName().lower()[2:] in geogs)

    def cleanupPage(self):
        ...

    def get_selected_geogs(self):
        return {w.objectName().lower()[2:] for w in self.geogWidgets if w.isChecked()}
