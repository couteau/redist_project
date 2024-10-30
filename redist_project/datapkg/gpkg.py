"""QGIS Redistricting Project Plugin - GeoPackage Utility Functions

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
import pathlib
import sqlite3
from typing import Union

from .utils import spatialite_connect

CREATE_GPKG_SQL = """
SELECT gpkgCreateBaseTables();
PRAGMA user_version=0x000028a0;
CREATE TABLE gpkg_ogr_contents (
    table_name    TEXT NOT NULL PRIMARY KEY,
    feature_count INTEGER DEFAULT NULL
);
"""
CREATE_GPKG_OGR_CONTENTS_INSERT_TRIGGER_SQL = """
CREATE TRIGGER trigger_insert_feature_count_{table}
AFTER INSERT ON {table}
BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 
        WHERE lower(table_name) = lower('{table}'); END;
"""


CREATE_GPKG_OGR_CONTENTS_DELETE_TRIGGER_SQL = """
CREATE TRIGGER trigger_delete_feature_count_{table}
AFTER DELETE ON {table}
BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 
        WHERE lower(table_name) = lower('{table}'); END;
"""


def createGeoPackage(gpkg: Union[str, pathlib.Path]) -> tuple[bool, Union[Exception, None]]:
    """Create a new GeoPackage file, deleting existing file if present

    Arguments:
        gpkg {Union[str, pathlib.Path]} -- the path to the GeoPackage file to create

    Returns:
        tuple[bool, Union[Exception, None]] -- tuple of success and, on failure, the exception that occurred
    """
    try:
        if isinstance(gpkg, str):
            gpkg = pathlib.Path(gpkg)

        if gpkg.exists():
            pattern = gpkg.name + '*'
            for f in gpkg.parent.glob(pattern):
                f.unlink()
        else:
            gpkg.touch()

        with spatialite_connect(gpkg, isolation_level="EXCLUSIVE") as db:
            db.execute("BEGIN EXCLUSIVE")
            db.executescript(CREATE_GPKG_SQL)
    except (sqlite3.Error, sqlite3.DatabaseError, sqlite3.OperationalError) as e:
        return False, e

    return True, None


def createGpkgTable(
        gpkg: Union[str, pathlib.Path, sqlite3.Connection],
        table: str,
        create_table_sql: str,
        geom_column_name: str = 'geom',
        geom_type: str = 'MULTIPOLYGON',
        srid: int = -1,
        create_spatial_index=True,
        add_featurecount_triggers=True
):
    try:
        if isinstance(gpkg, sqlite3.Connection):
            db = gpkg
        else:
            db = spatialite_connect(gpkg)

        db.executescript(create_table_sql)
        if srid is None:
            srid = 0

        if srid not in (-1, 0):
            if db.execute(f'SELECT count(*) FROM gpkg_spatial_ref_sys WHERE srs_id={srid}').fetchone()[0] == 0:
                db.execute(f'SELECT gpkgInsertEpsgSRID({srid})')
        db.execute(f"SELECT gpkgAddGeometryColumn('{table}', '{geom_column_name}', '{geom_type}', 0 , 0, {srid})")
        db.execute(f"SELECT gpkgAddGeometryTriggers('{table}', '{geom_column_name}')")

        if create_spatial_index:
            db.execute(f"SELECT gpkgAddSpatialIndex('{table}', '{geom_column_name}')")

        if add_featurecount_triggers:
            db.execute(f"INSERT INTO gpkg_ogr_contents (table_name) VALUES ('{table}')")
            db.execute(CREATE_GPKG_OGR_CONTENTS_INSERT_TRIGGER_SQL.format(table=table))
            db.execute(CREATE_GPKG_OGR_CONTENTS_DELETE_TRIGGER_SQL.format(table=table))

    except (sqlite3.Error, sqlite3.DatabaseError, sqlite3.OperationalError) as e:
        return False, e

    return True, None
