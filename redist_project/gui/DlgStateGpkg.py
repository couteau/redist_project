from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog,
    QWidget
)

from ..core.settings import settings
from ..core.state import State
from ..datapkg.utils import cvap_years
from ..datapkg.vr import validate_vr
from .ui.DlgStateGpkg import Ui_dlgDownloadStateGpkg


class DlgStateGpkg(Ui_dlgDownloadStateGpkg, QDialog):
    def __init__(self, state: State, parent: QWidget | None = None, flags: Qt.WindowFlags | Qt.WindowType = Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setupUi(self)
        self.state = state

        self.lbIntro.setText(self.lbIntro.text().format(state=state.name))
        self.rbStandardPackage.setText(self.rbStandardPackage.text().format(state=state.name))
        self.rbCustomPackage.setText(self.rbCustomPackage.text().format(state=state.name))
        self.cmDecennialYear.currentIndexChanged.connect(self.populateCVAPYears)
        self.populateCVAPYears()

        self.cbIncludeCVAP.toggled.connect(self.validateDialog)
        self.cmCVAPYear.currentIndexChanged.connect(self.validateDialog)
        self.cbIncludeVoterReg.toggled.connect(self.validateDialog)
        self.fwL2VRData.fileChanged.connect(self.validateDialog)
        self.cbIncludeVoterReg.toggled.connect(self.clearVRPath)

    def populateCVAPYears(self):
        self.cmCVAPYear.clear()
        self.cmCVAPYear.addItems(
            cvap_years(self.cmDecennialYear.currentText())
        )
        self.cmCVAPYear.setCurrentText(self.state.year)

    def clearVRPath(self):
        if not self.cbIncludeVoterReg.isChecked():
            self.fwL2VRData.setFilePath("")

    def validateDialog(self):
        valid = True
        if self.cbIncludeCVAP.isChecked():
            valid = self.cmCVAPYear.currentIndex() != -1

        if valid and self.cbIncludeVoterReg.isChecked():
            if self.fwL2VRData.filePath() == "":
                valid = False
            else:
                valid = validate_vr(self.fwL2VRData.filePath(), self.state.id, "2020")
            if isinstance(valid, ValueError):
                settings.iface.messageBar().pushWarning("Invalid Voter Registration file", str(valid))
                valid = False

        self.buttonBox.button(self.buttonBox.Ok).setEnabled(valid)
