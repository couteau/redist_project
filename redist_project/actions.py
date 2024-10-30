"""QGIS Redistricting Project Plugin - actions

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
from typing import (
    TYPE_CHECKING,
    Callable,
    Optional,
    Union
)

from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtGui import QIcon

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QAction
else:
    from qgis.PyQt.QtWidgets import QAction


class RedistProjectActions(QObject):
    _instance: "RedistProjectActions" = None
    _actions: dict

    def __new__(cls, owner: Optional[QObject] = None):
        if cls._instance is None:
            cls._instance = super(RedistProjectActions, cls).__new__(cls, owner)
            cls._instance._actions = {}

        return cls._instance

    def createAction(
        self,
        name: str,
        icon: Union[QIcon, str],
        text: str,
        tooltip: Optional[str] = None,
        callback: Optional[Callable] = None,  # pylint: disable=deprecated-typing-alias
        parent: Optional[QObject] = None
    ) -> QAction:
        if isinstance(icon, str):
            icon = QIcon(icon)

        action = QAction(icon, text, parent or self)
        if isinstance(tooltip, str):
            action.setToolTip(tooltip)
        if callback is not None:
            action.triggered.connect(callback)

        self._actions[name] = action
        return action

    def __getattr__(self, key: str) -> QAction:
        if key in self._actions:
            return self._actions[key]

        raise AttributeError()

    def __getitem__(self, key: str) -> QAction:
        if key in self._actions:
            return self._actions[key]

        raise IndexError()
