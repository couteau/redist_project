

import os

from qgis.gui import QgsFileWidget
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLineEdit,
    QRadioButton,
    QWizardPage
)

from ...core.settings import settings
from ...datapkg.vr import validate_vr


class WzpStateGpkg(QWizardPage):
    def setupUi(self):
        # pylint: disable=attribute-defined-outside-init
        self.rbStandardPackage = self.findChild(QRadioButton, "rbStandardPackage")
        self.rbCustomPackage = self.findChild(QRadioButton, "rbCustomPackage")
        self.edPackageName = self.findChild(QLineEdit, "edPackageName")
        self.cmDecennialYear = self.findChild(QComboBox, "cmDecennialYear")
        self.cbIncludeCVAP = self.findChild(QCheckBox, "cbIncludeCVAP")
        self.cmCVAPYear = self.findChild(QComboBox, "cmCVAPYear")
        self.cbIncludeVoterReg = self.findChild(QCheckBox, "cbIncludeVoterReg")
        self.fwL2VRData = self.findChild(QgsFileWidget, "fwL2VRData")
        self.rbCustomPackage.toggled.connect(self.completeChanged)
        self.edPackageName.textChanged.connect(self.completeChanged)
        self.cbIncludeCVAP.stateChanged.connect(self.completeChanged)
        self.cmCVAPYear.currentIndexChanged.connect(self.completeChanged)
        self.cbIncludeVoterReg.stateChanged.connect(self.completeChanged)
        self.fwL2VRData.fileChanged.connect(self.completeChanged)

    def isComplete(self) -> bool:
        valid = True
        if self.edPackageName.isVisible() and not self.edPackageName.text():
            valid = False

        if self.cbIncludeCVAP.isChecked():
            valid = valid and self.cmCVAPYear.currentIndex() != -1

        if valid and self.cbIncludeVoterReg.isChecked():
            if self.fwL2VRData.filePath() == "":
                valid = False
            elif not os.path.exists(self.fwL2VRData.filePath()) or not os.path.isfile(self.fwL2VRData.filePath()):
                valid = False
            else:
                valid_vr = validate_vr(
                    self.fwL2VRData.filePath(),
                    self.wizard().state.code,
                    self.cmDecennialYear.currentText()
                )

                if isinstance(valid_vr, Exception):
                    if isinstance(valid_vr, ValueError):
                        settings.iface.messageBar().pushWarning("Invalid Voter Registration file", str(valid_vr))
                    valid = False

        return valid
