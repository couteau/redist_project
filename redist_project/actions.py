from typing import (
    Callable,
    Optional,
    Self,
    Union
)

from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction


class RedistProjectActions(QObject):
    _instance: "RedistProjectActions" = None
    _actions: dict

    def __new__(cls, owner: Optional[QObject] = None) -> Self:
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
