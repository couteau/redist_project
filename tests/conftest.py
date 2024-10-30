"""Redistricting Project Generator - test fixtures

Copyright 2022-2024, Stuart C. Naifeh

QGIS app fixtures, Copyright (C) 2021-2023 pytest-qgis Contributors, used
and modified under GNU General Public License version 3


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
import contextlib
import os
import pathlib
import shutil
import tempfile
import unittest.mock
from collections.abc import Generator
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
    overload
)

import pytest
from pytest_mock import MockerFixture
from qgis.core import (
    QgsApplication,
    QgsLayerTree,
    QgsLayerTreeModel,
    QgsMapLayer,
    QgsProject,
    QgsRelationManager,
    QgsVectorLayer
)
from qgis.gui import (
    Qgis,
    QgisInterface,
    QgsGui,
    QgsLayerTreeView,
    QgsMapCanvas,
    QgsMessageBarItem
)
from qgis.PyQt import (
    QtCore,
    QtWidgets,
    sip
)

from redist_project.core.state import StateList

if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest

# pylint: disable=redefined-outer-name, unused-argument, protected-access


try:
    _QGIS_VERSION = Qgis.versionInt()
except AttributeError:
    _QGIS_VERSION = Qgis.QGIS_VERSION_INT

_APP: Optional[QgsApplication] = None
_CANVAS: Optional[QgsMapCanvas] = None
_IFACE: Optional[QgisInterface] = None
_PARENT: Optional[QtWidgets.QWidget] = None
_QGIS_CONFIG_PATH: Optional[pathlib.Path] = None

CANVAS_SIZE = (600, 600)


class MockMessageBar(QtCore.QObject):
    """Mocked message bar to hold the messages."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: dict[int, list[str]] = {
            Qgis.MessageLevel.Info: [],
            Qgis.MessageLevel.Warning: [],
            Qgis.MessageLevel.Critical: [],
            Qgis.MessageLevel.Success: [],
        }

    def get_messages(self, level: int) -> list[str]:
        """Used to test which messages have been logged."""
        return self.messages[level]

    @overload
    @staticmethod
    def createMessage(text: Optional[str], parent: Optional[QtWidgets.QWidget] = None):
        ...

    @overload
    @staticmethod
    def createMessage(title: str, text: str, parent: Optional[QtWidgets.QWidget] = None):
        ...

    @overload
    @staticmethod
    def createMessage(widget: QtWidgets.QWidget, parent: Optional[QtWidgets.QWidget] = None):
        ...

    @staticmethod
    def createMessage(title: Union[str, QtWidgets.QWidget], text: Union[str, QtWidgets.QWidget, None] = None, parent: Optional[QtWidgets.QWidget] = None):
        if isinstance(text, QtWidgets.QWidget):
            parent = text
            text = None

        if isinstance(title, QtWidgets.QWidget):
            item = QgsMessageBarItem(title, parent=parent)
        elif isinstance(title, str) and isinstance(text, str):
            item = QgsMessageBarItem(title, text, parent=parent)
        else:
            item = QgsMessageBarItem(title, parent=parent)

        return item

    @overload
    def pushMessage(  # noqa: N802
        self,
        text: str,
        level: int = Qgis.MessageLevel.Info,
        duration: int = -1,  # noqa: ARG002
    ) -> None:
        ...

    @overload
    def pushMessage(
        self,
        title: str,
        text: str,
        level: int = Qgis.MessageLevel.Info,
        duration: int = -1
    ) -> None:
        ...

    @overload
    def pushMessage(  # noqa: N802
        self,
        title: str,
        text: str,
        showMore: Optional[str] = None,
        level: int = Qgis.MessageLevel.Info,
        duration: int = -1,  # noqa: ARG002
    ) -> None:
        ...

    def pushMessage(  # noqa: N802
        self,
        title: str,
        message: Union[str, int],
        showMore: Union[str, int, None] = None,
        level: int = Qgis.MessageLevel.Info,
        duration: int = -1,  # noqa: ARG002
    ) -> None:
        """A mocked method for pushing a message to the bar."""
        if isinstance(message, int):
            title = ""
            level = message or level
            duration = showMore or duration
            text = title
        else:
            text = message
            if not isinstance(showMore, str):
                level = showMore or level
                duration = level
                showMore = None

        msg = f"{title}:{text}"
        self.messages[level].append(msg)

    def pushCritical(self, title: str, message: str):
        self.pushMessage(title, message, Qgis.MessageLevel.Critical)

    def pushInfo(self, title: str, message: str):
        self.pushMessage(title, message, Qgis.MessageLevel.Info)

    def pushSuccess(self, title: str, message: str):
        self.pushMessage(title, message, Qgis.MessageLevel.Success)

    def pushWarning(self, title: str, message: str):
        self.pushMessage(title, message, Qgis.MessageLevel.Warning)

    def pushWidget(self, widget: Optional[QtWidgets.QWidget], level: Qgis.MessageLevel = Qgis.MessageLevel.Info, duration: int = 0):
        if widget is None:
            return None

        return QgsMessageBarItem(widget, level, duration)


class MockQgisInterface(QgisInterface):
    initializationCompleted = QtCore.pyqtSignal()
    projectRead = QtCore.pyqtSignal()
    newProjectCreated = QtCore.pyqtSignal()
    layerSavedAs = QtCore.pyqtSignal("PyQt_PyObject", str)
    currentLayerChanged = QtCore.pyqtSignal()

    def __init__(self, canvas: QgsMapCanvas, parent: QtWidgets.QMainWindow):
        super().__init__()
        self.setParent(parent)
        self._canvases = [canvas]
        self._layers: list[QgsMapLayer] = []
        self._toolbars: dict[str, QtWidgets.QToolBar] = {}

        model = QgsLayerTreeModel(QgsProject.instance().layerTreeRoot(), parent)
        self._layerTreeView = QgsLayerTreeView(parent)
        self._layerTreeView.setModel(model)
        self._layerTreeView.currentLayerChanged.connect(self.currentLayerChanged)
        self._activeLayerId = None
        self._messageBar = MockMessageBar()
        QgsProject.instance().layersAdded.connect(self.addLayers)
        QgsProject.instance().removeAll.connect(self.removeAllLayers)

    def layerTreeView(self):
        return self._layerTreeView

    def mapCanvas(self):
        return self._canvases[0]

    def mapCanvases(self):
        return self._canvases

    def createNewMapCanvas(self, name: str):
        self._canvases.append(QgsMapCanvas(self.parent()))
        self._canvases[-1].setObjectName(name)
        return self._canvases[-1]

    def closeMapCanvas(self, name: str):
        canvas = self.parent().findChild(QgsMapCanvas, name)
        if canvas is not None:
            self._canvases.remove(canvas)
            canvas.hide()
            canvas.deleteLater()

    def messageBar(self):
        return self._messageBar

    @QtCore.pyqtSlot("QList<QgsMapLayer*>")
    def addLayers(self, layers: list[QgsMapLayer]) -> None:
        """Handle layers being added to the registry so they show up in canvas.

        :param layers: list<QgsMapLayer> list of map layers that were added

        .. note:: The QgsInterface api does not include this method,
            it is added here as a helper to facilitate testing.
        """
        current_layers = self._canvases[0].layers()
        final_layers = []
        for layer in current_layers:
            final_layers.append(layer)
        for layer in layers:
            final_layers.append(layer)
        self._layers = final_layers

        self._canvases[0].setLayers(final_layers)

    @QtCore.pyqtSlot()
    def removeAllLayers(self) -> None:
        """Remove layers from the canvas before they get deleted."""
        if not sip.isdeleted(self._canvases[0]):
            self._canvases[0].setLayers([])
        self._layers = []

    def newProject(self, promptToSaveFlag: bool = False) -> None:
        """Create new project."""
        # noinspection PyArgumentList
        instance = QgsProject.instance()
        instance.removeAllMapLayers()
        root: QgsLayerTree = instance.layerTreeRoot()
        root.removeAllChildren()
        relation_manager: QgsRelationManager = instance.relationManager()
        for relation in relation_manager.relations():
            relation_manager.removeRelation(relation)
        self._layers = []
        self.newProjectCreated.emit()
        return True

    def addVectorLayer(
        self, path: str, base_name: str, provider_key: str
    ) -> QgsVectorLayer:
        """Add a vector layer.

        :param path: Path to layer.
        :type path: str

        :param base_name: Base name for layer.
        :type base_name: str

        :param provider_key: Provider key e.g. 'ogr'
        :type provider_key: str
        """
        layer = QgsVectorLayer(path, base_name, provider_key)
        self.addLayers([layer])
        return layer

    def activeLayer(self) -> Optional[QgsMapLayer]:
        """Get pointer to the active layer (layer selected in the legend)."""
        return (
            QgsProject.instance().mapLayer(self._activeLayerId)
            if self._activeLayerId
            else None
        )

    def setActiveLayer(self, layer: QgsMapLayer) -> None:
        """
        Set the active layer (layer gets selected in the legend)
        """
        self._activeLayerId = layer.id()
        self.currentLayerChanged.emit()

    def iconSize(self) -> QtCore.QSize:
        return QtCore.QSize(24, 24)

    def mainWindow(self) -> QtWidgets.QMainWindow:
        return self.parent()

    def addToolBar(self, toolbar: Union[str, QtWidgets.QToolBar]) -> QtWidgets.QToolBar:
        """Add toolbar with specified name.

        :param toolbar: Name for the toolbar or QToolBar object.
        """
        if isinstance(toolbar, str):
            name = toolbar
            _toolbar = QtWidgets.QToolBar(name, parent=self.parent())
        else:
            name = toolbar.windowTitle()
            _toolbar = toolbar
        self._toolbars[name] = _toolbar
        return _toolbar

    def editableLayers(self, modified=False):
        return [l for l in self._layers if l.isEditable() and (l.isModified() or not modified)]

    layerTreeCanvasBridge = unittest.mock.MagicMock()

    zoomFull = unittest.mock.MagicMock()
    zoomToPrevious = unittest.mock.MagicMock()
    zoomToNext = unittest.mock.MagicMock()
    zoomToActiveLayer = unittest.mock.MagicMock()

    addRasterLayer = unittest.mock.MagicMock()
    addMeshLayer = unittest.mock.MagicMock()
    addVectorTileLayer = unittest.mock.MagicMock()
    addPointCloudLayer = unittest.mock.MagicMock()
    addTiledSceneLayer = unittest.mock.MagicMock()

    addPluginToMenu = unittest.mock.MagicMock()
    addToolBarIcon = unittest.mock.MagicMock()
    removeToolBarIcon = unittest.mock.MagicMock()

    projectMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)

    projectImportExportMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)
    addProjectImportAction = unittest.mock.MagicMock()
    removeProjectImportAction = unittest.mock.MagicMock()

    editMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)
    viewMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)
    layerMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)
    newLayerMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)
    addLayerMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)
    settingsMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)
    pluginMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)
    pluginHelpMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)
    rasterMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)
    databaseMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)
    vectorMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)

    def firstRightStandardMenu(self):
        return QtWidgets.QMenu(_PARENT)

    windowMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)
    helpMenu = unittest.mock.MagicMock(spec=QtWidgets.QMenu)

    fileToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    layerToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    dataSourceManagerToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    mapNavToolToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    digitizeToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    advancedDigitizeToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    shapeDigitizeToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    attributesToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    selectionToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    pluginToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    helpToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    rasterToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    vectorToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    databaseToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)
    webToolBar = unittest.mock.MagicMock(spec=QtWidgets.QToolBar)

    mapToolActionGroup = unittest.mock.MagicMock(spec=QtWidgets.QActionGroup)

    openDataSourceManagerPage = unittest.mock.MagicMock()

    addCustomActionForLayerType = unittest.mock.MagicMock()
    removeCustomActionForLayerType = unittest.mock.MagicMock()
    addCustomActionForLayer = unittest.mock.MagicMock()

    addPluginToVectorMenu = unittest.mock.MagicMock()
    removePluginVectorMenu = unittest.mock.MagicMock()

    addDockWidget = unittest.mock.MagicMock()
    removeDockWidget = unittest.mock.MagicMock()
    registerMainWindowAction = unittest.mock.MagicMock()
    unregisterMainWindowAction = unittest.mock.MagicMock()

    registerOptionsWidgetFactory = unittest.mock.MagicMock()
    unregisterOptionsWidgetFactory = unittest.mock.MagicMock()
    registerProjectPropertiesWidgetFactory = unittest.mock.MagicMock()
    unregisterProjectPropertiesWidgetFactory = unittest.mock.MagicMock()

    actionNewProject = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionOpenProject = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSaveProject = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSaveProjectAs = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSaveMapAsImage = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionProjectProperties = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionCreatePrintLayout = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionShowLayoutManager = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionExit = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionCutFeatures = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionCopyFeatures = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionPasteFeatures = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddFeature = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionDeleteSelected = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionMoveFeature = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSplitFeatures = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSplitParts = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddRing = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddPart = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSimplifyFeature = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionDeleteRing = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionDeletePart = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionVertexTool = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionVertexToolActiveLayer = unittest.mock.MagicMock(spec=QtWidgets.QAction)

    actionPan = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionPanToSelected = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionZoomIn = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionZoomOut = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSelect = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSelectRectangle = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSelectPolygon = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSelectFreehand = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSelectRadius = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionIdentify = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionFeatureAction = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionMeasure = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionMeasureArea = unittest.mock.MagicMock(spec=QtWidgets.QAction)

    actionZoomFullExtent = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionZoomToLayers = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionZoomToSelected = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionZoomLast = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionZoomNext = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionZoomActualSize = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionMapTips = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionNewBookmark = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionShowBookmarks = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionDraw = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionNewVectorLayer = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddOgrLayer = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddRasterLayer = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddPgLayer = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddWmsLayer = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddXyzLayer = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddVectorTileLayer = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddPointCloudLayer = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddAfsLayer = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddAmsLayer = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionCopyLayerStyle = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionPasteLayerStyle = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionOpenTable = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionOpenFieldCalculator = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionOpenStatisticalSummary = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionToggleEditing = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSaveActiveLayerEdits = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAllEdits = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSaveEdits = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionSaveAllEdits = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionRollbackEdits = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionRollbackAllEdits = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionCancelEdits = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionCancelAllEdits = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionLayerSaveAs = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionDuplicateLayer = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionLayerProperties = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddToOverview = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAddAllToOverview = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionRemoveAllFromOverview = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionHideAllLayers = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionShowAllLayers = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionHideSelectedLayers = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionToggleSelectedLayers = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionToggleSelectedLayersIndependently = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionHideDeselectedLayers = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionShowSelectedLayers = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionManagePlugins = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionPluginListSeparator = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionShowPythonDialog = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionToggleFullScreen = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionOptions = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionCustomProjection = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionHelpContents = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionQgisHomePage = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionCheckQgisVersion = unittest.mock.MagicMock(spec=QtWidgets.QAction)
    actionAbout = unittest.mock.MagicMock(spec=QtWidgets.QAction)


def _init_qgis():
    global _APP, _CANVAS, _IFACE, _PARENT, _QGIS_CONFIG_PATH  # noqa: PLW0603 # pylint: disable=global-statement

    # Use temporary path for QGIS config
    _QGIS_CONFIG_PATH = pathlib.Path(tempfile.mkdtemp(prefix="pytest-qgis"))

    os.environ["QGIS_CUSTOM_CONFIG_PATH"] = str(_QGIS_CONFIG_PATH)
    # os.environ["QT_QPA_PLATFORM"] = "offscreen"

    _APP = QgsApplication([], GUIenabled=True)
    _APP.initQgis()
    QgsGui.editorWidgetRegistry().initEditors()
    QgsProject.instance().legendLayersAdded.connect(_APP.processEvents)

    _PARENT = QtWidgets.QMainWindow()
    _CANVAS = QgsMapCanvas(_PARENT)
    _PARENT.resize(QtCore.QSize(CANVAS_SIZE[0], CANVAS_SIZE[1]))
    _CANVAS.resize(QtCore.QSize(CANVAS_SIZE[0], CANVAS_SIZE[1]))
    _IFACE = MockQgisInterface(_CANVAS, _PARENT)

    if _QGIS_VERSION >= 31800:
        from qgis.utils import \
            iface  # noqa: F401 # pylint: disable=unused-import, import-outside-toplevel # This import is required

        unittest.mock.patch("qgis.utils.iface", _IFACE).start()


# inititalize the QGIS application on loading module --
# waiting until plugin initialization may result in application
# modules loading with an uninitialized QGIS application
_init_qgis()


@pytest.fixture(autouse=True, scope="session")
def qgis_app(request: "SubRequest") -> Generator[QgsApplication, Any, Any]:
    yield _APP

    assert _APP
    QgsProject.instance().legendLayersAdded.disconnect(_APP.processEvents)
    if not sip.isdeleted(_CANVAS) and _CANVAS is not None:
        _CANVAS.deleteLater()
    _APP.exitQgis()
    if _QGIS_CONFIG_PATH and _QGIS_CONFIG_PATH.exists():
        with contextlib.suppress(PermissionError):
            shutil.rmtree(_QGIS_CONFIG_PATH)


@pytest.fixture(scope="session")
def qgis_parent(qgis_app: QgsApplication) -> QtWidgets.QWidget:  # noqa: ARG001
    return _PARENT


@pytest.fixture(scope="session")
def qgis_canvas() -> QgsMapCanvas:
    assert _CANVAS
    return _CANVAS


@pytest.fixture(scope="session")
def qgis_iface() -> QgisInterface:
    assert _IFACE
    return _IFACE


@pytest.fixture
def qgis_new_project(qgis_iface: QgisInterface) -> None:
    """
    Initializes new QGIS project by removing layers and relations etc.
    """
    qgis_iface.newProject()


@pytest.fixture
def datadir(tmp_path: pathlib.Path, mocker: MockerFixture):
    d = tmp_path / 'data'
    s = pathlib.Path(__file__).parent / 'data'
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(s, d)
    settings = mocker.patch("redist_project.core.settings.settings")
    settings.datapath = d
    mocker.patch("redist_project.core.state.settings", new=settings)
    yield d
    shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture
def cachedir(datadir: pathlib.Path) -> pathlib.Path:
    d = datadir / 'cache'
    if not d.exists():
        d.mkdir()
    return datadir / 'cache'


@pytest.fixture
def state_list_2020():
    return StateList("2020")
