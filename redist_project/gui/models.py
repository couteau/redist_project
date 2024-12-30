"""QGIS Redistricting Project Plugin - Qt Model/View Models
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

from qgis.PyQt.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    QVariant
)

from ..core.state import (
    State,
    StateList
)
from ..core.utils import tr

columns = ["id", "package_name", "fips", "stusab"]


class StateListModel(QAbstractTableModel):
    def __init__(self, state_list: StateList, parent: QObject = None):
        super().__init__(parent)
        self._state_list = state_list

    @property
    def state_list(self):
        return self._state_list

    @state_list.setter
    def state_list(self, value: StateList):
        self.beginResetModel()
        self._state_list = value
        self.endResetModel()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 4 if not parent.isValid() else 0

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self._state_list.row_count() if not parent.isValid() else 0

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        col = index.column()

        if role in {Qt.DisplayRole, Qt.EditRole}:
            try:
                return self._state_list[row, columns[col]]
            except IndexError:
                pass

        return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):  # pylint: disable=unused-argument
        return QVariant()


class GeographyListModel(QAbstractTableModel):
    def __init__(self, state: State, excluded_geogs: Iterable[str] = None, parent: QObject = None):
        super().__init__(parent)
        self.exclude = set(excluded_geogs) \
            if excluded_geogs is not None else {"b", "bg", "t", "vtd"}
        self._state = None
        self.geographies = []
        self.state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value: State):
        if self._state != value:
            self.beginResetModel()
            self._state = value
            if self._state:
                self.geographies = [
                    g for g in self._state.get_geographies().values()
                    if g.geog not in self.exclude
                ]
            else:
                self.geographies = []
            self.endResetModel()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 3 if not parent.isValid() else 0

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.geographies)

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        col = index.column()

        if role in {Qt.DisplayRole, Qt.EditRole}:
            if 0 <= row < len(self.geographies):
                geog = self.geographies[row]
                if col == 0:
                    return geog.name
                if col == 1:
                    return geog.descrip
                if col == 2:
                    return geog.level

        return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        header = QVariant()
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    header = tr("Table Name")
                elif section == 1:
                    header = tr("Geography")
                elif section == 2:
                    header = tr("Sumary Level")
            else:
                header = self.geographies[section].geog

        return header


class SubdivisionListModel(QAbstractTableModel):
    def __init__(self, state: State, geog: str, parent: QObject = None):
        super().__init__(parent)
        self._state = None
        self._geog = None
        self.subdivisions = []
        self.state = state
        self.geog = geog

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value: State):
        if value != self._state:
            self.beginResetModel()
            self._state = value

            if self._state and self._geog:
                self.subdivisions = self._state.get_subdivisions(self._geog)
            else:
                self.subdivisions = []
            self.endResetModel()

    @property
    def geog(self):
        return self._geog

    @geog.setter
    def geog(self, value: str):
        if value != self._geog:
            self.beginResetModel()
            self._geog = value
            if self._state and self._geog:
                self.subdivisions = self._state.get_subdivisions(self._geog)
            else:
                self.subdivisions = []
            self.endResetModel()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 2 if not parent.isValid() else 0

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0

        return len(self.subdivisions)

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        col = index.column()

        if role in {Qt.DisplayRole, Qt.EditRole}:
            if 0 <= row < len(self.subdivisions):
                sd = self.subdivisions[row]
                if col == 0:
                    return sd.geoid
                if col == 1:
                    return sd.name

        return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):  # pylint: disable=unused-argument
        header = QVariant()
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    header = "GeoID"
                elif section == 1:
                    header = tr("Name")

        return header
