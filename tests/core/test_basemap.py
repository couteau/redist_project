import os
import sys

import pytest
from qgis.core import (
    QgsApplication,
    QgsAuthMethodConfig,
    QgsProject
)
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QMenu
from qgis.utils import (
    loadPlugin,
    plugins,
    startPlugin
)

from redist_project.core.basemaps import BaseMapRegistry

# pylint: disable=unused-argument


class TestBaseMap:
    @pytest.fixture(scope='session')
    def auth_db(self):
        configdir = os.environ['QGIS_CUSTOM_CONFIG_PATH']
        authdb_path = os.path.join(configdir, 'qgis-auth.db')
        os.environ['QGIS_AUTH_DB_DIR_PATH'] = authdb_path
        am = QgsApplication.authManager()
        am.setMasterPassword('dummy', True)
        am.init(QgsApplication.pluginPath(), authdb_path)
        return am

    @pytest.fixture(scope='session')
    def maptiler(self, auth_db, session_mocker):
        assert loadPlugin('qgis-maptiler-plugin')
        assert startPlugin('qgis-maptiler-plugin')
        session_mocker.patch.object(sys.modules['qgis-maptiler-plugin.maptiler'].QMetaObject, 'invokeMethod')
        return plugins['qgis-maptiler-plugin']

    @pytest.mark.parametrize(('basemap', 'layers'), [
        ('Basic', 2),
        ('Bright', 2),
        ('Dataviz', 2),
        ('OpenStreetMap', 2),
        ('Outdoor', 5),
        ('Streets', 2),
        ('Toner', 2),
        ('Topo', 4)
    ])
    def test_add_maptiler_basemap(self, basemap, layers, maptiler):
        key = os.environ['MAPTILER_API_KEY']
        settings = QSettings()
        cfg = QgsAuthMethodConfig('MapTilerHmacSha256')
        cfg.setName('qgis-maptiler-plugin')
        cfg.setConfigMap({'token': key})
        am = QgsApplication.authManager()
        (res, cfg) = am.storeAuthenticationConfig(cfg, True)
        if res:
            settings.beginGroup('/maptiler')
            settings.setValue('auth_cfg_id', cfg.id())
            settings.endGroup()

        BaseMapRegistry.create_layer(('MapTilerProvider', basemap))
        assert len(QgsProject.instance().mapLayers()) == layers

    def test_add_vectortiles_basemap(self):
        # create a connection in the Vector Tiles provider
        settings = QSettings()
        settings.setValue('connections/vector-tile/items/Esri Basemap/authcfg', '')
        settings.setValue('connections/vector-tile/items/Esri Basemap/password', '')
        settings.setValue('connections/vector-tile/items/Esri Basemap/referer', '')
        settings.setValue('connections/vector-tile/items/Esri Basemap/service-type', '')
        settings.setValue('connections/vector-tile/items/Esri Basemap/url',
                          'https://basemaps.arcgis.com/arcgis/rest/services/World_Basemap_GCS_v2/VectorTileServer/tile/{z}/{y}/{x}.pbf')
        settings.setValue('connections/vector-tile/items/Esri Basemap/styleUrl',
                          'https://www.arcgis.com/sharing/rest/content/items/2c2be6e056a54901965be11752b83dfe/resources/styles/root.json')
        settings.setValue('connections/vector-tile/items/Esri Basemap/username', '')
        settings.setValue('connections/vector-tile/items/Esri Basemap/zmax', "14")
        settings.setValue('connections/vector-tile/items/Esri Basemap/zmin', "0")

        QgsProject.instance().removeAllMapLayers()
        BaseMapRegistry.create_layer(('Vector Tiles', 'Esri Basemap'))
        assert len(QgsProject.instance().mapLayers()) == 1

    def test_add_hcmgis_basemap(self):
        assert loadPlugin('HCMGIS')
        assert startPlugin('HCMGIS')

        m: QMenu = plugins["HCMGIS"].vectortiles_menu
        for i in m.actions():
            if not i.isSeparator() and not i.menu() and "Vietnam" not in i.text():
                QgsProject.instance().removeAllMapLayers()
                BaseMapRegistry.create_layer(('HCMGIS', id(i)))
                assert len(QgsProject.instance().mapLayers()) == 1
