# -*- coding: utf-8 -*-
"""Redistricting Project Generator

    Create GeoPackage database with standard set of tables with 
    standardized field names

        begin                : 2023-08-14
        copyright            : (C) 2023 by Cryptodira
        email                : stuart@cryptodira.org
        git sha              : $Format:%H$

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
from pathlib import Path
from typing import Callable

from osgeo import (
    gdal,
    ogr
)
from redistricting.core.utils import spatialite_connect

from . import sql


def import_shape(shp_path: str | Path, gpkg: str | Path, progress: Callable = None, filter=None):
    gdal.UseExceptions()

    if isinstance(shp_path, str):
        shp_path = Path(shp_path)

    layer_name = shp_path.stem[3:]

    if isinstance(gpkg, str):
        gpkg = Path(gpkg)

    src_ds: ogr.DataSource = ogr.Open(str(shp_path), False)
    if src_ds is None:
        print(
            f"Unable to open datasource `{shp_path:s}'."
        )
        return 1

    dest_ds: ogr.DataSource = None
    dest_driver: ogr.Driver = None

    with ogr.ExceptionMgr(useExceptions=False), gdal.quiet_errors():
        dest_ds: ogr.DataSource = ogr.Open(str(gpkg), True)

    if dest_ds is None:
        # see if we can open it in non-update mode
        with ogr.ExceptionMgr(useExceptions=False), gdal.quiet_errors():
            dest_ds: ogr.DataSource = ogr.Open(str(gpkg), False)
        if dest_ds is not None:
            dest_ds.delete()
            dest_ds = None

    if dest_ds is None:
        dest_driver = ogr.GetDriverByName('GPKG')
        if dest_driver is None:
            print("Unable to find driver `GPKG'.")
            return 1
        if not dest_driver.TestCapability(ogr.ODrCCreateDataSource):
            print("GPKG driver does not support data source creation.")
            return 1

        dest_ds = dest_driver.CreateDataSource(str(gpkg))
        if dest_ds is None:
            print(f"GPKG driver failed to create {gpkg:s})")
            return 1

    src_layer: ogr.Layer = src_ds.GetLayer()
    if src_layer is None:
        print("FAILURE: Couldn't fetch layer!")
        return 1

    if filter is not None:
        if src_layer.SetAttributeFilter(filter) != 0:
            print(f"FAILURE: SetAttributeFilter({filter}) failed.")
            return 1

    total = src_layer.GetFeatureCount()
    src_feat_defn: ogr.FeatureDefn = src_layer.GetLayerDefn()
    dest_crs = src_layer.GetSpatialRef()

    # Delete output layer if it already exists
    gdal.PushErrorHandler("CPLQuietErrorHandler")
    dest_layer: ogr.Layer = dest_ds.GetLayerByName(layer_name)
    gdal.PopErrorHandler()
    gdal.ErrorReset()

    if dest_layer is not None:
        if dest_ds.DeleteLayer(dest_layer.GetName()) != 0:
            print("DeleteLayer() failed when overwrite requested.")
            return None

        dest_layer = None

    # Create output layer
    gdal.ErrorReset()
    dest_layer = dest_ds.CreateLayer(
        layer_name, dest_crs, ogr.wkbMultiPolygon,
        ['GEOMETRY_NAME=geom', 'SPATIAL_INDEX=YES', 'OVERWRITE=YES']
    )
    if dest_layer is None:
        print("Unable to create destination layer")
        return 1

    src_field_count = src_feat_defn.GetFieldCount()
    field_map = list(range(src_field_count))

    for f in range(src_field_count):
        src_field_defn: ogr.FieldDefn = src_feat_defn.GetFieldDefn(f)
        dest_field_defn = ogr.FieldDefn(
            src_field_defn.GetNameRef(), src_field_defn.GetType()
        )
        dest_field_defn.SetWidth(src_field_defn.GetWidth())
        dest_field_defn.SetPrecision(src_field_defn.GetPrecision())

        if dest_layer.CreateField(dest_field_defn) != 0:
            print(
                f"Could not add output field {dest_field_defn.GetNameRef()}!"
            )
            return 1

    src_layer.ResetReading()
    src_feature: ogr.Feature
    chunk_size = 200
    count = 0
    if chunk_size > 0:
        dest_layer.StartTransaction()

    while src_feature := src_layer.GetNextFeature():
        gdal.ErrorReset()
        dest_feature = ogr.Feature(dest_layer.GetLayerDefn())
        if dest_feature.SetFromWithMap(src_feature, 1, field_map) != 0:
            if chunk_size > 0:
                dest_layer.RollbackTransaction()

            print(
                f"Unable to translate feature {src_feature.GetFID()} from layer {src_layer.GetName()}"
            )

            return 1

        dest_feature.SetFID(src_feature.GetFID())
        dest_geom: ogr.Geometry = dest_feature.GetGeometryRef()
        if dest_geom is not None:
            dest_geom.AssignSpatialReference(dest_crs)
            if dest_geom.GetGeometryType() == ogr.wkbPolygon:
                dest_feature.SetGeometryDirectly(
                    ogr.ForceToMultiPolygon(dest_geom)
                )

        gdal.ErrorReset()
        if dest_layer.CreateFeature(dest_feature) != 0:
            print(
                f"Unable to create feature {src_feature.GetFID()} in destination layer"
            )
            if chunk_size > 0:
                dest_layer.RollbackTransaction()

            return 1

        count = count + 1
        if chunk_size:
            if count % chunk_size == 0:
                dest_layer.CommitTransaction()
                dest_layer.StartTransaction()

                if progress:
                    progress(count, total)
        else:
            if progress:
                progress(count, total)

    if chunk_size:
        dest_layer.CommitTransaction()
        if progress:
            progress(count, total)

    dest_ds.Destroy()
    src_ds.Destroy()

    return 0


def import_state(st_prefix, gpkg_path, src_path, dec_year='2020', acs_year='2021', vr_date=None, progress: Callable = None):
    dec_yy = dec_year[2:]
    acs_yy = acs_year[2:]
    for table in sql.PL_TABLES:
        if progress:
            progress(msg=f"Importing {table}...")
        pl_shp_path = f"{st_prefix}_pl{dec_year}_{sql.PL_TABLES[table]}/{st_prefix}_pl{dec_year}_{sql.PL_TABLES[table]}.shp"
        cvap_src_table = sql.CVAP_TABLES[table].format(
            dec_year=dec_year,
            acs_year=acs_year
        )
        acs_data_path = f"{st_prefix}_cvap_{acs_year}_{sql.CVAP_TABLES[table].format(dec_year=dec_year, acs_year=acs_year)}/{st_prefix}_cvap_{acs_year}_{cvap_src_table}"

        if (Path(src_path) / pl_shp_path).exists():
            if progress:
                progress(
                    msg=f"Importing PL data from {st_prefix}_pl{dec_year}_{sql.PL_TABLES[table]}.shp..."
                )
            import_shape(Path(src_path) / pl_shp_path, gpkg_path, progress)
            with spatialite_connect(gpkg_path) as db:
                s = sql.create_table_script(table, dec_year)
                db.executescript(s)
                s = sql.insert_data_script(table, dec_year)

                # getattr(sql, f"insert_{table}_data").format(
                #    dec_yyyy=dec_year, dec_yy=dec_yy)
                db.executescript(s)
        else:
            continue

        acs_path = None
        if (Path(src_path) / f"{acs_data_path}.csv").exists():
            acs_path = Path(src_path) / f"{acs_data_path}.csv"
        elif (Path(src_path) / f"{acs_data_path}.shp").exists():
            acs_path = Path(src_path) / f"{acs_data_path}.shp"

        if acs_path:
            if progress:
                progress(
                    msg=f"Importing CVAP data from {acs_path.name}..."
                )
            import_shape(Path(src_path) / acs_path, gpkg_path, progress)
            with spatialite_connect(gpkg_path) as db:
                n = db.execute(
                    f"SELECT length(geoid20) FROM {acs_path.stem[3:]} LIMIT 1"
                ).fetchone()[0]
                if n == sql.GEOID_LEN[table] - 1:
                    db.execute(
                        f"UPDATE {acs_path.stem[3:]} SET geoid20 = '0' || geoid20"
                    )

        with spatialite_connect(gpkg_path) as db:
            s = sql.add_cvap_fields.format(
                table=table, dec_yyyy=dec_year, dec_yy=dec_yy, acs_yyyy=acs_year, acs_yy=acs_yy
            )
            db.executescript(s)
            s = getattr(sql, f"insert_cvap_data_{table}", getattr(sql, 'insert_cvap_data')).format(
                table=table, src_table=cvap_src_table, dec_yyyy=dec_year, dec_yy=dec_yy, acs_yyyy=acs_year, acs_yy=acs_yy, geoid="geoid20"
            )
            db.executescript(s)

        if vr_date:
            l2_data = src_path / f"{st_prefix.upper()}_L2_{dec_year}BlockAgg" / \
                f"{st_prefix.upper()}_l2_{dec_year}block_agg_{vr_date}.csv"
            if l2_data.exists():
                import_shape(l2_data, gpkg_path, progress)
            with spatialite_connect(gpkg_path) as db:
                s = sql.add_vr_fields.format(
                    table=table, dec_yy=dec_yy, vr_date=vr_date
                )
                db.executescript(s)
                s = getattr(sql, 'insert_vr_data').format(
                    table=table, src_table='b', dec_yyyy=dec_year, dec_yy=dec_yy, vr_date=vr_date
                )
                db.executescript(s)
