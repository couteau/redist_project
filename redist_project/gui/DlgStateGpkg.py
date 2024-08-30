"""QGIS Redistricting Project Plugin - Configure or Download GeoPackage
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
import pathlib
from typing import (
    Any,
    Optional,
    Union
)

from qgis.core import (
    Qgis,
    QgsMessageLog
)
from qgis.PyQt.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    QVariant
)
from qgis.PyQt.QtWidgets import (
    QFileDialog,
    QHeaderView,
    QWidget,
    QWizard
)

from ..core.settings import settings
from ..core.state import State
from ..datapkg.bef import BEFData
from ..datapkg.geography import geographies
from ..datapkg.utils import cvap_years
from ..datapkg.vr import validate_vr
from .DlgAddBEF import AddBlockEquivalencyFileDialog
from .ui.WizStateGpkg import Ui_WizRedistrictingGpkg


class BEFModel(QAbstractTableModel):
    COL_NAMES = ["filepath", "joinField", "addFields"]
    COL_LABELS = ["BEF File", "Join Field", "Add Fields"]

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.befs: list[BEFData] = []

    def addBEFData(self, data: BEFData):
        self.beginInsertRows(QModelIndex(), len(self.befs), len(self.befs))
        self.befs.append(data)
        self.endInsertRows()

    def removeBEFData(self, row: int):
        self.beginRemoveRows(QModelIndex(), row, row)
        del self.befs[row]
        self.endRemoveRows()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0

        return len(self.befs)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0

        return 3

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.COL_LABELS[section]

        return QVariant()

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                value = str(self.befs[row].filepath)
            elif col == 1:
                value = self.befs[row].joinField
            elif col == 2:
                value = ','.join("{1}={0}".format(*v) for v in self.befs[row].addFields.items())
            else:
                value = QVariant()
        else:
            value = QVariant()

        return value


class ShapefileModel(QAbstractTableModel):
    def __init__(self, year: str, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.shapes: list[dict[str, Any]] = []
        self.year = year

    def addShape(self, path: str, layerName: str = None):
        self.beginInsertRows(QModelIndex(), len(self.shapes), len(self.shapes))
        layerName = layerName or pathlib.Path(path).stem
        self.shapes.append({"layerName": layerName, "filepath": path})
        self.endInsertRows()

    def removeShape(self, row: int):
        self.beginRemoveRows(QModelIndex(), row, row)
        del self.shapes[row]
        self.endRemoveRows()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0

        return len(self.shapes)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0

        return 2

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return "Layer Name" if section == 0 else "ShapeFile Path"

        return QVariant()

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        row = index.row()
        if role in (Qt.DisplayRole, Qt.EditRole):
            fld = "layerName" if index.column() == 0 else "filepath"
            return self.shapes[row][fld]

        return QVariant()

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if role == Qt.EditRole and index.column() == 0 and isinstance(value, str):
            for g in geographies.values():
                if value == f"{g.name}{self.year[-2:]}":
                    QgsMessageLog.logMessage("Layer name must be unique in GeoPackage", "Redistricting", Qgis.Critical)
                    return False
            for s in self.shapes:
                if s != self.shapes[index.row()] and s["layerName"] == value:
                    QgsMessageLog.logMessage("Layer name must be unique in GeoPackage", "Redistricting", Qgis.Critical)
                    return False

            self.shapes[index.row()]["layerName"] = value

            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)
        if index.column() == 0:
            flags |= Qt.ItemIsEditable | Qt.ItemIsEnabled

        return flags


class AcquireStateGpkgDialog(Ui_WizRedistrictingGpkg, QWizard):
    def __init__(
        self,
        state: State,
        custom: bool = False,
        parent: Optional[QWidget] = None,
        flags: Union[Qt.WindowFlags, Qt.WindowType] = Qt.WindowFlags()
    ):
        super().__init__(parent, flags)
        self.setupUi(self)
        self.wzpStateGpkg.setupUi()
        self.state = state

        self.wzpStateGpkg.setFinalPage(True)
        self.wzpAddlBEFs.setFinalPage(True)
        if custom:
            self.rbCustomPackage.setChecked(True)
            self.rbStandardPackage.hide()
            self.rbCustomPackage.hide()
        else:
            self.lbPackageName.hide()
            self.edPackageName.hide()

        self.wzpStateGpkg.setSubTitle(self.wzpStateGpkg.subTitle().format(state=state.name))
        self.rbStandardPackage.setText(self.rbStandardPackage.text().format(state=state.name))
        self.rbCustomPackage.setText(self.rbCustomPackage.text().format(state=state.name))
        self.rbCustomPackage.toggled.connect(self.button(self.NextButton).setEnabled)
        self.cmDecennialYear.currentIndexChanged.connect(self.populateCVAPYears)
        self.populateCVAPYears()

        self.cmCVAPYear.currentIndexChanged.connect(self.cvapYearChanged)
        self.cbIncludeVoterReg.toggled.connect(self.clearCVAPYear)
        self.fwL2VRData.fileChanged.connect(self.vrPathChanged)
        self.cbIncludeVoterReg.toggled.connect(self.clearVRPath)

        self.befModel = BEFModel(self)
        self.vwAddlBEFs.setModel(self.befModel)
        self.vwAddlBEFs.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.vwAddlBEFs.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.shpModel = ShapefileModel(self.cmDecennialYear.currentText(), self)
        self.vwAddlShapeFiles.setModel(self.shpModel)
        self.vwAddlShapeFiles.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.btnAddBEF.clicked.connect(self.addBEF)
        self.btnRemoveBEF.clicked.connect(self.removeBEF)
        self.btnAddShapeFile.clicked.connect(self.addShape)
        self.btnRemoveShapeFile.clicked.connect(self.removeShape)

    @property
    def addlEquivalencies(self):
        return self.befModel.befs

    @property
    def addlShapefiles(self) -> dict[str, str]:
        return {d["layerName"]: d["filepath"] for d in self.shpModel.shapes}

    def populateCVAPYears(self):
        if self.state.custom_id is not None:
            self.state.year = self.cmDecennialYear.currentText()

        self.cmCVAPYear.clear()
        self.cmCVAPYear.addItems(
            cvap_years(self.cmDecennialYear.currentText())
        )
        self.cmCVAPYear.setCurrentIndex(-1)
        self.cbIncludeCVAP.setChecked(False)

    def clearCVAPYear(self):
        if not self.cbIncludeCVAP.isChecked():
            self.cmCVAPYear.setCurrentIndex(-1)

    def cvapYearChanged(self):
        if self.cmCVAPYear.currentIndex() != -1:
            self.cbIncludeCVAP.setChecked(True)

    def clearVRPath(self):
        if not self.cbIncludeVoterReg.isChecked():
            self.fwL2VRData.setFilePath("")

    def vrPathChanged(self):
        if self.fwL2VRData.filePath() and pathlib.Path(self.fwL2VRData.filePath()).exists():
            self.cbIncludeVoterReg.setChecked(True)

    def validateCurrentPage(self) -> bool:
        valid = True
        if self.edPackageName.isVisible() and not self.edPackageName.text():
            valid = False

        if self.cbIncludeCVAP.isChecked():
            valid = valid and self.cmCVAPYear.currentIndex() != -1

        if valid and self.cbIncludeVoterReg.isChecked():
            if self.fwL2VRData.filePath() == "":
                valid = False
            else:
                valid = valid and validate_vr(self.fwL2VRData.filePath(), self.state.code, "2020")

            if isinstance(valid, ValueError):
                settings.iface.messageBar().pushMessage("Invalid Voter Registration file", str(valid), 3)
                valid = False

        return valid

    def addBEF(self):
        dlg = AddBlockEquivalencyFileDialog(self)
        if dlg.exec() == dlg.Accepted:
            data = dlg.befData()
            if data is not None:
                self.befModel.addBEFData(data)

    def removeBEF(self):
        idx = self.vwAddlBEFs.currentIndex()
        if idx.isValid():
            self.befModel.removeBEFData(idx.row())

    def addShape(self):
        dlg = QFileDialog(self)
        dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
        dlg.setNameFilter("*.shp")
        if dlg.exec() == dlg.Accepted:
            for file in dlg.selectedFiles():
                self.shpModel.addShape(file)

    def removeShape(self):
        idx = self.vwAddlShapeFiles.currentIndex()
        if idx.isValid():
            self.shpModel.removeShape(idx.row())
