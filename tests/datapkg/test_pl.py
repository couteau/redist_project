import pathlib
import sqlite3
import zipfile

import geopandas as gpd
import pytest
from pytest_mock import MockerFixture

from redist_project.datapkg.geography import geographies
from redist_project.datapkg.pl import (
    create_block_df,
    create_df_for_geog,
    create_table_script,
    download_and_extract_pl,
    download_shapefiles,
    join_pl_to_shape,
    load_pl_data,
    load_shape,
    make_shape,
    spatialite_connect
)


class TestPL:

    def test_download_pl(self, cachedir: pathlib.Path, mocker: MockerFixture):
        progress = mocker.MagicMock()
        download_and_extract_pl('de', '2020', cachedir, progress)
        assert (cachedir / 'de2020.pl.zip').exists()
        assert progress.called

    def test_download_shapefiles(self, cachedir: pathlib.Path, mocker: MockerFixture):
        progress = mocker.MagicMock()
        download_shapefiles('de', '2020', ['b'], cachedir, progress)
        assert (cachedir / 'tl_2020_10_tabblock20.zip').exists()
        assert progress.called

    def test_load_pl_data(self, cachedir: pathlib.Path):
        with zipfile.ZipFile(cachedir / 'ri2020.pl.zip', 'r') as z:
            z.extractall(cachedir)

        df = load_pl_data('ri', '2020', cachedir)
        assert not df.empty
        assert df.shape == (36800, 396)

        with zipfile.ZipFile(cachedir / 'ri2010.pl.zip', 'r') as z:
            z.extractall(cachedir)

        df = load_pl_data('ri', '2010', cachedir)
        assert not df.empty
        assert df.shape == (30769, 391)

    def test_load_shape(self, cachedir: pathlib.Path):
        df = load_shape('ri', '2020', 'vtd', cachedir)
        assert df is not None and not df.empty

    @pytest.mark.parametrize('dec_year', ('2010', '2020'))
    def test_join_pl_to_shape(self, dec_year, cachedir: pathlib.Path):
        with zipfile.ZipFile(cachedir / f'ri{dec_year}.pl.zip', 'r') as z:
            z.extractall(cachedir)

        pl = load_pl_data('ri', dec_year, cachedir)
        shp = load_shape('ri', dec_year, 'c', cachedir)
        df = join_pl_to_shape(shp, dec_year, 'c', pl)
        assert isinstance(df, gpd.GeoDataFrame)
        assert not df.empty

    def test_create_block_df(self, cachedir: pathlib.Path):
        with zipfile.ZipFile(cachedir / 'ri2010.pl.zip', 'r') as z:
            z.extractall(cachedir)

        with zipfile.ZipFile(cachedir / 'tl_2010_44_tabblock10.zip', 'r') as z:
            z.extractall(cachedir)

        df = load_pl_data('ri', '2010', cachedir)
        bdf = create_block_df('ri', '2010', df, cachedir)
        assert len(bdf) == 25181

    @pytest.mark.parametrize('dec_year', ('2010', '2020'))
    def test_make_shapefile(self, dec_year, cachedir: pathlib.Path):
        with zipfile.ZipFile(cachedir / f'ri{dec_year}.pl.zip', 'r') as z:
            z.extractall(cachedir)

        with zipfile.ZipFile(cachedir / f'tl_{dec_year}_44_tabblock{dec_year[-2:]}.zip', 'r') as z:
            z.extractall(cachedir)

        df = load_pl_data('ri', dec_year, cachedir)
        bdf = create_block_df('ri', dec_year, df, cachedir)
        for g in ("bg", "aiannh"):
            s = make_shape(g, bdf)
            assert s is not None

    @pytest.mark.parametrize('dec_year', ('2010', '2020'))
    def test_make_shapefile_with_full_block_df(self, dec_year, cachedir: pathlib.Path):
        with zipfile.ZipFile(cachedir / f'ri{dec_year}.pl.zip', 'r') as z:
            z.extractall(cachedir)

        with zipfile.ZipFile(cachedir / f'tl_{dec_year}_44_tabblock{dec_year[-2:]}.zip', 'r') as z:
            z.extractall(cachedir)

        df = load_pl_data('ri', dec_year, cachedir)
        bdf = create_df_for_geog('ri', dec_year, 'b', df, cachedir)
        for g in ("bg", "aiannh"):
            s = make_shape(g, bdf)
            assert s is not None

    def test_make_shapefile_non_existant_geog(self, cachedir: pathlib.Path):
        with zipfile.ZipFile(cachedir / 'ri2010.pl.zip', 'r') as z:
            z.extractall(cachedir)

        with zipfile.ZipFile(cachedir / 'tl_2010_44_tabblock10.zip', 'r') as z:
            z.extractall(cachedir)

        df = load_pl_data('ri', '2010', cachedir)
        bdf = create_block_df('ri', '2010', df, cachedir)
        s = make_shape("vtd", bdf)
        assert s is None

    def test_create_table_script(self):
        for dec_year in ('2010', '2020'):
            for g in geographies:
                sql = create_table_script(g, dec_year)
                stmts = sql.split(';')
                failed = []

                with spatialite_connect(":memory:") as temp_db:
                    for stmt in stmts:
                        try:
                            temp_db.execute(stmt)
                        except sqlite3.Error:
                            failed.append(stmt)

                assert len(failed) == 0
