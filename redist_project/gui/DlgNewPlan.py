# -*- coding: utf-8 -*-
"""QGIS Redistricting Project Plugin - New Plan Dialog

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
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QWizard
)
from redistricting.gui.wzpeditplandetails import dlgEditPlanDetailsPage
from redistricting.models import (
    RdsDataField,
    RdsPlan,
    deserialize
)

from ..core.fields import all_fields
from ..core.state import State
from ._dlgNewProjectFieldsPage import DlgNewProjectFieldsPage


class NewPlanDialog(QWizard):

    def __init__(self, state: State, plan: RdsPlan = None, parent=None):
        super().__init__(parent)
        self._plan = plan
        self.state = state
        self.new = True

        self.setWindowTitle(self.tr("New Redistricting Plan"))
        self.wizardStyle = QWizard.ModernStyle
        self.setOptions(QWizard.NoBackButtonOnStartPage |
                        QWizard.CancelButtonOnLeft |
                        QWizard.NoDefaultButton |
                        QWizard.HaveFinishButtonOnEarlyPages |
                        QWizard.HaveHelpButton |
                        QWizard.HelpButtonOnRight |
                        QWizard.HaveCustomButton1)
        self.setButtonText(QWizard.CustomButton1, "Advanced")
        self.customButtonClicked.connect(self.advancedClicked)

        self.addPage(dlgEditPlanDetailsPage(self))
        self.setField("numDistricts", plan.numDistricts)
        self.setField("numSeats", plan.numDistricts)

        self.fields_page = DlgNewProjectFieldsPage(self)
        # QWizard does not allow setting arbitrary fields -- only QWizardPages
        # can set fields and they must be based on a QWidget, so we have to create
        # dummy widgets and add them to a QWizardPage for fields that the page expects
        include_vap = QCheckBox(self.fields_page)
        include_vap.setChecked("vap_total" in plan.popFields)
        self.fields_page.layout().addChildWidget(include_vap)
        self.fields_page.registerField("include-vap", include_vap)
        include_vap.hide()

        include_cvap = QCheckBox(self.fields_page)
        include_cvap.setChecked("cvap_total" in plan.popFields)
        self.fields_page.layout().addChildWidget(include_cvap)
        self.fields_page.registerField("include-cvap", include_cvap)
        include_cvap.hide()

        include_vr = QCheckBox(self.fields_page)
        include_vr.setChecked("reg_total" in plan.popFields)
        self.fields_page.layout().addChildWidget(include_vr)
        self.fields_page.registerField("include-vr", include_vr)
        include_vr.hide()

        self.addPage(self.fields_page)
        self.fields_page.state = state
        if self._plan:
            self.fields_page.fields = [g.field for g in self._plan.dataFields]

    @property
    def planName(self):
        return self.field("planName")

    @property
    def description(self):
        return self.field("description")

    @property
    def numDistricts(self):
        return self.field("numDistricts")

    @property
    def numSeats(self):
        return self.field("numSeats")

    @property
    def gpkgPath(self):
        return self.field('gpkgPath')

    @property
    def dataFields(self):
        fields = self.fields_page.fields

        if not self.field("include-vap"):
            fields = [f for f in fields if all_fields[f]["pctbase"] != "vap_total"]

        if not self.field("include-cvap"):
            fields = [f for f in fields if all_fields[f]["pctbase"] != "cvap_total"]

        if not self.field("include-vr"):
            fields = [f for f in fields if all_fields[f]["pctbase"] != "reg_total"]

        result = []
        for f in fields:
            fld = deserialize(RdsDataField, {"field": f, "layer": self._plan.popLayer.id()} | all_fields[f])
            if fld:
                result.append(fld)
        return result

    def isComplete(self):
        for pageId in self.pageIds():
            if not self.page(pageId).isComplete():
                return False
        return True

    def advancedClicked(self, which: int):  # pylint: disable=unused-argument
        self.done(2)
