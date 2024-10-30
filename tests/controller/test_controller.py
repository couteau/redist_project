import pytest
from pytest_mock import MockerFixture
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QDialog
from qgis.utils import plugins
from redistricting.models import RdsPlan
from redistricting.redistricting import Redistricting

from redist_project.controller.projectctlr import ProjectController
from redist_project.gui.DlgNewProject import NewProjectDialog

# pylint: disable=unused-argument


class TestController:
    @pytest.fixture
    def mock_redist_plugin(self, qgis_iface, mocker: MockerFixture):
        settings = mocker.patch('redistricting.redistricting.QSettings')
        settings_obj = settings.return_value
        settings_obj.value.return_value = 'en_US'

        plugins["redistricting"] = mocker.patch(
            "redist_project.controller.projectctlr.Redistricting",
            spec=Redistricting(qgis_iface)
        )
        return plugins["redistricting"]

    @pytest.fixture
    def controller(self, qgis_iface, qgis_parent, mock_redist_plugin):
        return ProjectController(qgis_iface, qgis_parent)

    def test_create(self, qgis_iface, qgis_parent):
        c = ProjectController(qgis_iface, qgis_parent)
        assert c is not None

    def test_load(self, controller):
        controller.load()
        controller.unload()

    def test_readprojectparams(self, controller: ProjectController, datadir):
        QgsProject.instance().read(str(datadir / 'rhode_island.qgz'))
        assert controller.readProjectParams()
        assert controller.state == controller.states['2020']['ri']
        assert controller.year == '2020'
        assert isinstance(controller.template, RdsPlan)

        controller.clearProjectParams()
        QgsProject.instance().read(str(datadir / 'rhode_island_std_project.qgz'))
        assert not controller.readProjectParams()
        assert controller.state is None
        assert controller.year is None
        assert controller.template is None

    def test_readproject(self, controller: ProjectController, datadir):
        controller.load()

        QgsProject.instance().read(str(datadir / 'rhode_island.qgz'))
        assert controller.state == controller.states['2020']['ri']
        assert controller.year == '2020'
        assert isinstance(controller.template, RdsPlan)

        QgsProject.instance().read(str(datadir / 'rhode_island_std_project.qgz'))
        assert controller.state is None
        assert controller.year is None
        assert controller.template is None

        QgsProject.instance().read(str(datadir / 'rhode_island.qgz'))
        assert controller.state == controller.states['2020']['ri']
        assert controller.year == '2020'
        assert isinstance(controller.template, RdsPlan)

        QgsProject.instance().clear()
        assert controller.state is None
        assert controller.year is None
        assert controller.template is None

        controller.unload()

    @pytest.fixture
    def mock_newproject_dialog(self, mocker: MockerFixture, state_list_2020):
        dlg: NewProjectDialog = mocker.patch(
            'redist_project.controller.projectctlr.NewProjectDialog', spec=NewProjectDialog)
        dlg.return_value.state = state_list_2020['ri']
        dlg.return_value.numDistricts = 3
        dlg.return_value.numSeats = 3
        dlg.return_value.deviation = 0.05
        dlg.return_value.includeVAP = True
        dlg.return_value.includeCVAP = False
        dlg.return_value.includeVR = False
        dlg.return_value.geographies = ['b', 'c', 'vtd', 'p']
        dlg.return_value.subdivision_geog = None
        dlg.return_value.subdivision_geoid = None
        dlg.return_value.dataFields = []
        dlg.return_value.baseMap = False
        dlg.return_value.customLayers = []
        dlg.return_value.exec.return_value = QDialog.Accepted
        return dlg

    def test_newproject(self, controller: ProjectController, mock_newproject_dialog, mocker: MockerFixture):
        build_project = mocker.patch('redist_project.controller.projectctlr.build_project')
        controller.newProject()
        mock_newproject_dialog.assert_called_once()
        build_project.assert_called_once()
