"""QGIS Redistricting Project Plugin - base map utilities

        begin                : 2024-10-28
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
import itertools
from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    NewType,
    Optional
)

from qgis.core import (
    QgsApplication,
    QgsDataCollectionItem,
    QgsLayerItem,
    QgsProject,
    QgsVectorTileLayer
)
from qgis.PyQt.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QObject,
    Qt
)
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import QMenu
from qgis.utils import plugins

from .utils import tr

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QAction
else:
    from qgis.PyQt.QtWidgets import QAction


BaseMapIndex = NewType("BaseMapIndex", tuple[str, Any])

BASEMAP_INDEX = Qt.UserRole + 1


class BaseMapProvider(QObject):
    @abstractmethod
    def name(self) -> str:
        return ""

    @abstractmethod
    def get_base_map_names(self) -> dict[str, str]:
        return {}

    @abstractmethod
    def create_layer(self, base_map_idx: str):
        ...


class VectorTilesProvider(BaseMapProvider):
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.items: dict[str, QgsLayerItem] = None
        self.provider = QgsApplication.dataItemProviderRegistry().provider('Vector Tiles')

    def name(self) -> str:
        if self.provider is None:
            return ""

        return self.provider.name()

    def get_base_map_names(self) -> dict[str, str]:
        if self.items is None:
            self.items: dict[str, QgsLayerItem] = {}

            if self.provider is not None:
                rootItem: QgsDataCollectionItem = self.provider.createDataItem("", None)
                for i in rootItem.createChildren():
                    self.items[i.name()] = i

        return {k: v.name() for k, v in self.items.items()}

    def create_layer(self, base_map_idx: str):
        if self.items is None:
            self.get_base_map_names()

        i = self.items.get(base_map_idx)
        if i is None:
            return

        layer = QgsVectorTileLayer(i.uri(), i.layerName())
        QgsProject.instance().addMapLayer(layer, True)


class HCMGISProvider(BaseMapProvider):
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.items: dict[str, QAction] = None

    def name(self) -> str:
        return "HCMGIS"

    def get_base_map_names(self) -> dict[str, str]:
        if "HCMGIS" in plugins:
            m: QMenu = plugins["HCMGIS"].vectortiles_menu
            self.items: dict[str, QAction] = {
                id(i): i for i in m.actions() if not i.isSeparator() and not i.menu() and "Vietnam" not in i.text()
            }
        else:
            self.items: dict[str, QAction] = {}

        return {k: v.text() for k, v in self.items.items()}

    def create_layer(self, base_map_idx: str):
        if self.items is None:
            self.get_base_map_names()

        action = self.items.get(base_map_idx, None)
        if action is not None:
            action.trigger()


class MapTilerProvider(BaseMapProvider):
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self.items: dict[str, QAction] = None

    def name(self):
        return "MapTiler"

    def get_base_map_names(self) -> dict[str, str]:
        if self.items is None:
            self.items: dict[str, QAction] = {}
            provider = QgsApplication.dataItemProviderRegistry().provider('MapTilerProvider')
            if provider is not None:
                rootItem: QgsDataCollectionItem = provider.createDataItem("", None)
                for i in rootItem.createChildren():
                    for a in i.actions(None):
                        if a.text() == 'Add as Vector':
                            a.setParent(self)
                            self.items[i.name()] = a

        return {k: k for k in self.items}

    def create_layer(self, base_map_idx: str):
        if self.items is None:
            self.get_base_map_names()

        action = self.items.get(base_map_idx, None)
        if action is not None:
            action.trigger()


class BaseMapRegistry:
    providers: dict[str, BaseMapProvider] = {
        "Vector Tiles": VectorTilesProvider(),
        'HCMGIS': HCMGISProvider(),
        'MapTilerProvider': MapTilerProvider()
    }

    @staticmethod
    def get_providers():
        return BaseMapRegistry.providers

    @staticmethod
    def create_layer(base_map_idx: BaseMapIndex):
        provider_name, idx = base_map_idx
        provider = BaseMapRegistry.providers[provider_name]
        provider.create_layer(idx)

    @staticmethod
    def add_provider(name: str, provider: BaseMapProvider):
        BaseMapRegistry.providers[name] = provider

    @staticmethod
    def remove_provider(name: str):
        if name in BaseMapRegistry.providers:
            del BaseMapRegistry.providers[name]

    @staticmethod
    def get_provider(name: str) -> BaseMapProvider:
        return BaseMapRegistry.providers.get(name, None)


class BaseMapProviderModel(QAbstractListModel):
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.keys = [(None, "Select")]
        self.items = [tr("Select base map provider...")]

        for k, p in BaseMapRegistry.get_providers().items():
            provider_items = p.get_base_map_names()
            if len(provider_items) == 0:
                continue

            self.keys.append((None, k))
            self.items.append(p.name())

            self.keys.extend(zip(itertools.repeat(k), provider_items.keys()))
            self.items.extend(provider_items.values())

    def rowCount(self, parent: QModelIndex):
        if parent.isValid():
            return 0

        return len(self.items)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        row = index.row()
        if role == Qt.DisplayRole:
            if self.keys[row][0] is None:
                v = self.items[row]
            else:
                v = "  " + self.items[row]
        elif role == Qt.FontRole and self.isSectionItem(row):
            v = QFont()
            v.setBold(True)
            v.setItalic(True)
        elif role == BASEMAP_INDEX and not self.isSectionItem(row):
            v = self.keys[row]
        else:
            v = None

        return v

    def isSectionItem(self, item: int):
        return self.keys[item][0] is None
