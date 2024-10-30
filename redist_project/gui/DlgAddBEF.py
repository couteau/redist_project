"""QGIS Redistricting Project Plugin - Add Equivalency File Dialog

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
import csv
import os
import pathlib
from typing import (
    Any,
    Optional,
    Union
)

from qgis.core import (
    Qgis,
    QgsField,
    QgsFields,
    QgsMessageLog,
    QgsVectorLayer
)
from qgis.PyQt.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    QVariant
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QWidget
)

from ..datapkg.bef import EquivalencyData
from .ui.DlgAddBEF import Ui_dlgAddBEF


class FieldSelectModel(QAbstractTableModel):
    COL_NAMES = ['field', 'col_name', 'type']
    COL_LABELS = ['Field', 'New Name', 'Type']

    def __init__(self, layer: QgsVectorLayer, joinField: QgsField, parent: Optional[QObject] = None):
        super().__init__(parent)
        with open(layer.source(), "rt", encoding="utf-8") as f:
            self.has_header = csv.Sniffer().has_header(f.read(4096))

        self._layer = layer
        self._fields = [{
            'field': f.name() if self.has_header else i,
            'col_name': f.name(),
            'type': f.friendlyTypeString(),
            'selected': True
        } for i, f in enumerate(self._layer.fields())]
        self._joinField: QgsField = joinField

    @property
    def joinField(self) -> QgsField:
        return self._joinField

    @joinField.setter
    def joinField(self, value: QgsField):
        if value != self._joinField:
            self.beginResetModel()
            self._joinField = value
            self.endResetModel()

    @property
    def joinIndex(self):
        return self._layer.fields().indexOf(self._joinField.name())

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0

        return len(self._fields) - 1

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return 3

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        row = index.row()

        if row >= self.joinIndex:
            row += 1

        if role in (Qt.DisplayRole, Qt.EditRole):
            col = self.COL_NAMES[index.column()]

            return self._fields[row][col]

        if role == Qt.CheckStateRole and index.column() == 0:
            return Qt.Checked if self._fields[row]["selected"] else Qt.Unchecked

        return QVariant()

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.DisplayRole) -> bool:
        row = index.row()

        if row >= self.joinIndex:
            row += 1

        if index.column() == 1 and role == Qt.EditRole and isinstance(value, str):
            if not value:
                QgsMessageLog.logMessage("Field name must be provided", "Redistricting", Qgis.Critical)
                return False

            if value[0].isdigit():
                value = "_" + value

            if not value.isidentifier():
                QgsMessageLog.logMessage("Field name is not a valid identifier", "Redistricting", Qgis.Critical)
                return False

            for f in self._fields:
                if f != self._fields[row] and f["col_name"] == value:
                    QgsMessageLog.logMessage("Field name must be unique", "Redistricting", Qgis.Critical)
                    return False

            self._fields[row]["col_name"] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True

        if index.column() == 0 and role == Qt.CheckStateRole:
            self._fields[row]["selected"] = value == Qt.Checked
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True

        return super().setData(index, value, role)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.COL_LABELS[section]

        return QVariant()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        row = index.row()

        if row >= self.joinIndex:
            row += 1

        f = super().flags(index)
        if index.column() == 0:
            f |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsEnabled
        elif index.column() == 1:
            f |= Qt.ItemIsEditable | Qt.ItemIsEnabled

        return f

    def selectAll(self):
        for bef in self._fields:
            bef["selected"] = True
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount() - 1, 0), [Qt.CheckStateRole])

    def selectNone(self):
        for bef in self._fields:
            bef["selected"] = False
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount() - 1, 0), [Qt.CheckStateRole])


class AddBlockEquivalencyFileDialog(Ui_dlgAddBEF, QDialog):
    def __init__(self, parent: Optional[QWidget] = None, flags: Union[Qt.WindowFlags, Qt.WindowType] = Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setupUi(self)

        self.befLayer: QgsVectorLayer = None
        self.model: FieldSelectModel = None
        self.fields: QgsFields = None

        self.fwBEFFile.fileChanged.connect(self.setBlockEquivalencyFile)
        self.cmbJoinField.currentIndexChanged.connect(self.updateJoinField)
        self.btnSelectAll.clicked.connect(self.selectAll)
        self.btnSelectNone.clicked.connect(self.selectNone)
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

    def setBlockEquivalencyFile(self):
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
        self.befLayer = None
        self.model = None

        if not os.path.exists(self.fwBEFFile.filePath()) or not os.path.isfile(self.fwBEFFile.filePath()):
            return

        try:
            self.befLayer = QgsVectorLayer(self.fwBEFFile.filePath())
            if not self.befLayer.isValid():
                return
        except ValueError:
            return

        self.fields = QgsFields(self.befLayer.fields())
        self.model = FieldSelectModel(self.befLayer, self.fields[0], self)
        self.cmbJoinField.setLayer(self.befLayer)

        self.vwFields.setModel(self.model)
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)

    def updateJoinField(self, index: int):
        self.model.joinField = self.fields[index]

    def befData(self):
        if self.befLayer is not None and self.model is not None:
            joinField = self.model._fields[self.cmbJoinField.currentIndex()]["field"]
            return EquivalencyData(
                pathlib.Path(self.befLayer.source()),
                joinField,
                {f["field"]: f["col_name"] for f in self.model._fields if f["selected"] and f["field"] != joinField}
            )

        return None

    def selectAll(self):
        if self.model is not None:
            self.model.selectAll()

    def selectNone(self):
        if self.model is not None:
            self.model.selectNone()
