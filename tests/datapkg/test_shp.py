import pytest
from pytest_mock import MockerFixture

import redist_project.core.buildpkg
from redist_project.datapkg.shp import import_shape
from redist_project.datapkg.utils import spatialite_connect


class TestShape:
    @pytest.mark.parametrize('shape', (
        'Urban_Areas_4879541579459676182.zip',
        'Urban_Areas_-4076954223611017438.geojson',
        'ri_dhc_2020_b.csv'
    ))
    def test_add_shape(self, datadir, shape, mocker: MockerFixture):
        settings = mocker.patch.object(redist_project.core.buildpkg, "settings")
        settings.datapath = datadir

        r = import_shape(
            datadir / 'rhode_island.gpkg',
            datadir / shape,
            'urban_areas'
        )
        assert r is not None

        with spatialite_connect(datadir / 'rhode_island.gpkg') as db:
            c = db.execute("SELECT * FROM sqlite_schema WHERE name = 'urban_areas' AND type = 'table'")
            assert c.fetchone()
