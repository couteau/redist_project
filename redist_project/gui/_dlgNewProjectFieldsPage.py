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
from collections.abc import Iterable
from typing import Any

from qgis.PyQt.QtCore import (
    QAbstractListModel,
    QMimeData,
    QModelIndex,
    QObject,
    Qt,
    QVariant
)
from qgis.PyQt.QtWidgets import QWizardPage

from ..core.fields import (
    cvap_fields,
    pop_fields,
    vap_fields,
    vr_fields
)
from ..core.state import State
from .ui.WzpAddFields import Ui_wzpAddFields


class FieldListModel(QAbstractListModel):
    def __init__(self, src_fields: dict[str, dict], fields: list[str], source=True, parent: QObject | None = None):
        super().__init__(parent)
        self.fields = fields
        self.src_fields = src_fields
        self.src_rows = [f for f in self.src_fields if f not in self.fields]
        self.source = source

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1 if not parent.isValid() else 0

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0

        if self.source:
            return len(self.src_fields) - len(self.fields)

        return len(self.fields)

    def endResetModel(self):
        self.src_rows = [f for f in self.src_fields if f not in self.fields]
        super().endResetModel()

    def data(self, index: QModelIndex, role: int = ...):
        if not index.isValid() or index.parent().isValid():
            return QVariant()

        if self.source:
            fld = self.src_rows[index.row()]
        else:
            fld = self.fields[index.row()]

        row = self.src_fields[fld]

        if role in {Qt.DisplayRole, Qt.EditRole}:
            try:
                return row["caption"]
            except KeyError:
                pass
        elif role == Qt.ToolTipRole:
            try:
                return row["tooltip"]
            except KeyError:
                pass

        return QVariant()

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if self.source:
            return False

        if role == Qt.DisplayRole:
            self.fields[index.row()] = value
            return True

        return super().setData(index, value, role)

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        if parent.isValid():
            return False

        self.beginInsertRows(parent, row, row+count-1)
        self.fields[row:row] = [""] * count
        self.endInsertRows()

        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        if parent.isValid():
            return False

        self.beginRemoveRows(parent, row, row + count - 1)
        del self.fields[row:row+count]
        self.endRemoveRows()

        return True

    def mimeTypes(self) -> list[str]:
        return ["text/x-redist-fieldlist"]

    def mimeData(self, indexes: Iterable[QModelIndex]) -> QMimeData:
        data = QMimeData()
        if self.source:
            lst = [f for f in self.src_fields.keys() if f not in self.fields]
        else:
            lst = self.fields
        flds = [lst[i.row()] for i in indexes if i.isValid()]
        data.setData("text/x-redist-fieldlist", ":".join(flds).encode())
        return data

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
        if parent.isValid():
            return False

        if column != 0:
            return False

        if action == Qt.IgnoreAction:
            return True

        if action != Qt.MoveAction:
            return False

        d: bytes = data.data("text/x-redist-fieldlist").data()
        flds = d.decode().split(":")
        if row == -1:
            row = len(self.fields)

        self.insertRows(row, len(flds), QModelIndex())
        for i, f in enumerate(flds):
            self.setData(
                self.index(row+i, 0, QModelIndex()),
                f,
                Qt.DisplayRole
            )
        row += len(flds)

        return True

    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.MoveAction

    def canDropMimeData(
        self,
        data: QMimeData,
        action: Qt.DropAction,
        row: int,               # pylint: disable=unused-argument
        column: int,            # pylint: disable=unused-argument
        parent: QModelIndex     # pylint: disable=unused-argument
    ) -> bool:
        if action != Qt.MoveAction or not data.hasFormat("text/x-redist-fieldlist"):
            return False

        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        f = super().flags(index)
        if index.isValid():
            f = f | Qt.ItemIsDragEnabled
        elif not self.source:
            f = f | Qt.ItemIsDropEnabled
        return f


class DlgNewProjectFieldsPage(Ui_wzpAddFields, QWizardPage):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.src_fields = {}
        self._fields = []
        self._state = None

        self.src_model = FieldListModel(
            self.src_fields, self._fields, True, self)
        self.dest_model = FieldListModel(
            self.src_fields, self._fields, False, self)

        self.lvSource.setModel(self.src_model)
        self.lvDest.setModel(self.dest_model)
        # self.lvSource.doubleClicked.connect(self.addSelected)
        self.lvSource.activated.connect(self.addCurrent)
        # self.lvDest.doubleClicked.connect(self.removeSelected)
        self.lvDest.activated.connect(self.removeCurrent)

        self.btnAdd.clicked.connect(self.addSelected)
        self.btnAddAll.clicked.connect(self.addAll)
        self.btnRemove.clicked.connect(self.removeSelected)
        self.btnRemoveAll.clicked.connect(self.removeAll)

    def initializePage(self):
        super().initializePage()
        self.state = self.wizard().state

    def cleanupPage(self):
        ...

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value: State):
        if self._state != value:
            self.src_model.beginResetModel()
            self.dest_model.beginResetModel()
            self.src_fields.clear()
            self._fields.clear()
            if value:
                self.src_fields.update(pop_fields)
                if self.field("include-vap"):
                    self.src_fields.update(vap_fields)
                if self.field("include-cvap") and value.has_cvap():
                    self.src_fields.update(cvap_fields)
                if self.field("include-vr") and value.has_vr():
                    self.src_fields.update(vr_fields)
            self.dest_model.endResetModel()
            self.src_model.endResetModel()
            self._state = value
            self.updateButtons()

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value: list[str]):
        self.src_model.beginResetModel()
        self.dest_model.beginResetModel()
        self._fields.clear()
        self._fields.extend(value)
        self.dest_model.endResetModel()
        self.src_model.endResetModel()
        self.updateButtons()

    def moveFields(self, add: bool, selected: list[int] | None = None):
        self.src_model.beginResetModel()
        self.dest_model.beginResetModel()
        fields = [f for f in self.src_fields if (f in self._fields) != add]
        if selected:
            fields = [f for n, f in enumerate(fields) if n in selected]

        if add:
            self._fields.extend(fields)
        else:
            for f in fields:
                self._fields.remove(f)
        self.dest_model.endResetModel()
        self.src_model.endResetModel()
        self.updateButtons()

    def updateButtons(self):
        self.btnAdd.setEnabled(len(self._fields) != len(self.src_fields) and len(self.lvSource.selectedIndexes()) > 0)
        self.btnAddAll.setEnabled(len(self._fields) != len(self.src_fields))
        self.btnRemove.setEnabled(bool(self._fields) and len(self.lvDest.selectedIndexes()) > 0)
        self.btnRemoveAll.setEnabled(bool(self._fields))

    def addSelected(self):
        self.moveFields(
            True,
            [i.row()for i in self.lvSource.selectedIndexes()]
        )

    def addAll(self):
        self.moveFields(True)

    def addCurrent(self, index: QModelIndex):
        self.moveFields(True, [index.row()])

    def removeSelected(self):
        self.moveFields(
            False,
            [i.row() for i in self.lvDest.selectedIndexes()]
        )

    def removeAll(self):
        self.moveFields(False)

    def removeCurrent(self, index: QModelIndex):
        self.moveFields(False, [index.row()])
