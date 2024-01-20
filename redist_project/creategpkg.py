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
from os import PathLike
from pathlib import Path
from typing import Callable

from networkx import truncated_cube_graph
from osgeo import (
    gdal,
    ogr
)
from redistricting.core.utils import spatialite_connect

from . import sql


class GeoPackageCreator:
    def __init__(self, st_prefix: str, gpkg_path: PathLike, src_path: PathLike, progress: Callable = None):
        self.st_prefix = st_prefix
        self.gpkg_path = Path(gpkg_path)
        self.src_path = Path(src_path)
        if progress:
            self.progress = progress
        else:
            self.progress = lambda *var, **kwvar: None
        self.src_tables = []

    def import_shape(self, shp_path, layer_name=None, filter=None):
        gdal.UseExceptions()

        if isinstance(shp_path, str):
            shp_path = Path(shp_path)

        layer_name = layer_name or shp_path.stem[3:]

        src_ds: ogr.DataSource = ogr.Open(str(shp_path), False)
        if src_ds is None:
            print(
                f"Unable to open datasource `{shp_path:s}'."
            )
            return None

        dest_ds: ogr.DataSource = None
        dest_driver: ogr.Driver = None

        with ogr.ExceptionMgr(useExceptions=False), gdal.quiet_errors():
            dest_ds: ogr.DataSource = ogr.Open(str(self.gpkg_path), True)

        if dest_ds is None:
            # see if we can open it in non-update mode
            with ogr.ExceptionMgr(useExceptions=False), gdal.quiet_errors():
                dest_ds: ogr.DataSource = ogr.Open(str(self.gpkg_path), False)
            if dest_ds is not None:
                dest_ds.delete()
                dest_ds = None

        if dest_ds is None:
            dest_driver = ogr.GetDriverByName('GPKG')
            if dest_driver is None:
                print("Unable to find driver `GPKG'.")
                return None
            if not dest_driver.TestCapability(ogr.ODrCCreateDataSource):
                print("GPKG driver does not support data source creation.")
                return None

            dest_ds = dest_driver.CreateDataSource(str(self.gpkg_path))
            if dest_ds is None:
                print(f"GPKG driver failed to create {self.gpkg_path:s})")
                return None

        src_layer: ogr.Layer = src_ds.GetLayer()
        if src_layer is None:
            print("FAILURE: Couldn't fetch layer!")
            return None

        if filter is not None:
            if src_layer.SetAttributeFilter(filter) != 0:
                print(f"FAILURE: SetAttributeFilter({filter}) failed.")
                return None

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
            return None

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
                return None

        dd: ogr.FeatureDefn = dest_layer.GetLayerDefn()
        result = [dd.GetFieldDefn(i).name for i in range(dd.GetFieldCount())]

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

                return None

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

                return None

            count = count + 1
            if chunk_size:
                if count % chunk_size == 0:
                    dest_layer.CommitTransaction()
                    dest_layer.StartTransaction()
                    self.progress(count, total)
            else:
                self.progress(count, total)

        if chunk_size:
            dest_layer.CommitTransaction()
            self.progress(count, total)

        dest_ds.Destroy()
        src_ds.Destroy()

        return result

    def join_csv(self, table, csv_path: PathLike, fields=None, add_fields=truncated_cube_graph()):
        if isinstance(csv_path, str):
            csv_path = Path(csv_path)

        f = self.import_shape(csv_path)
        if f is None:
            return None

        if fields is None:
            fields = f

        with spatialite_connect(self.gpkg_path) as db:
            layer_name = csv_path.stem[3:]
            if add_fields:
                tbl_info = db.execute(
                    f"pragma table_info('{layer_name}')").fetchall()
                crt_tbl_cols = [
                    f"{fld[1]} {fld[2]}{' NOT NULL' if fld[3] == 1 else ''}{f' DEFAULT {fld[4]}' if fld[4] is not None else ''}"
                    for fld in tbl_info
                    if fld[1] in fields]

                script = "\n".join(
                    [f"ALTER TABLE {table} ADD COLUMN {col};" for col in crt_tbl_cols])
                db.executescript(script)

            s = f"UPDATE {table} SET ({','.join([fields])}) = (SELECT {','.join(fields)} from {layer_name} src WHERE src.geoid20 = {table}.geoid)"
            db.execute(s)

    def add_vr_to_block(self, table: str, vr_date: str, dec_year: str):
        dec_yy = dec_year[2:]
        l2_data = Path(self.src_path) / f"{self.st_prefix.upper()}_L2_{dec_year}BlockAgg" / \
            f"{self.st_prefix.upper()}_l2_{dec_year}block_agg_{vr_date}.csv"
        if l2_data.exists():
            self.progress(
                msg=f"Importing voter registration data from {l2_data.name}..."
            )
            vr_fields = self.import_shape(l2_data)
            self.src_tables.append(l2_data.stem[3:])
            with spatialite_connect(self.gpkg_path) as db:
                s = sql.add_vr_fields.format(
                    table=table, dec_yy=dec_yy, vr_date=vr_date
                )
                db.executescript(s)
                s = getattr(sql, 'insert_vr_data').format(
                    vr_select=sql.make_vr_select(vr_fields),
                    table=table,
                    src_table='block_agg',
                    dec_yyyy=dec_year,
                    dec_yy=dec_yy,
                    vr_date=vr_date
                )
                db.executescript(s)

    def import_pl_geog(self, geog, dec_year):
        pl_shp_path = Path(self.src_path) / \
            f"{self.st_prefix}_pl{dec_year}_{sql.PL_TABLES[geog]}" / \
            f"{self.st_prefix}_pl{dec_year}_{sql.PL_TABLES[geog]}.shp"
        if not pl_shp_path.exists() and pl_shp_path.with_suffix('.csv').exists() and \
                (Path(self.src_path) / f"{self.st_prefix}_{dec_year}_{sql.PL_TABLES[geog]}_bound").exists():
            csv_path = pl_shp_path.with_suffix('.csv')
            pl_shp_path = Path(self.src_path) / \
                f"{self.st_prefix}_{dec_year}_{sql.PL_TABLES[geog]}_bound" / \
                f"{self.st_prefix}_{dec_year}_{sql.PL_TABLES[geog]}_bound.shp"
        else:
            csv_path = None

        if pl_shp_path.exists():
            self.progress(
                msg=f"Importing PL data from {self.st_prefix}_pl{dec_year}_{sql.PL_TABLES[geog]}.shp..."
            )
            self.import_shape(pl_shp_path)
            if csv_path:
                self.join_csv(f"{pl_shp_path.stem[3:]}", csv_path)

            self.src_tables.append(pl_shp_path.stem[3:])
            with spatialite_connect(self.gpkg_path) as db:
                s = sql.create_table_script(geog, dec_year)
                db.executescript(s)
                s = sql.insert_data_script(geog, dec_year)

                # getattr(sql, f"insert_{table}_data").format(
                #    dec_yyyy=dec_year, dec_yy=dec_yy)
                db.executescript(s)
            return True

        return False

    def import_cvap_geog(self, geog, dec_year='2020', acs_year='2021'):
        dec_yy = dec_year[2:]
        acs_yy = acs_year[2:]

        cvap_src_table = sql.CVAP_TABLES[geog].format(
            dec_year=dec_year,
            acs_year=acs_year
        )

        if sql.CVAP_TABLES[geog]:
            acs_data_path = f"{self.st_prefix}_cvap_{acs_year}_{cvap_src_table}/{self.st_prefix}_cvap_{acs_year}_{cvap_src_table}"
        else:
            acs_data_path = ""

        acs_path = None
        if acs_data_path:
            if (Path(self.src_path) / f"{acs_data_path}.csv").exists():
                acs_path = Path(self.src_path) / f"{acs_data_path}.csv"
            elif (Path(self.src_path) / f"{acs_data_path}.shp").exists():
                acs_path = Path(self.src_path) / f"{acs_data_path}.shp"

        do_import = acs_path is not None or geog != 'block'
        if acs_path:
            self.progress(msg=f"Importing CVAP data from {acs_path.name}...")
            self.import_shape(acs_path)
            self.src_tables.append(acs_path.stem[3:])
            with spatialite_connect(self.gpkg_path) as db:
                # fix any dropped leading 0 from geoid if necessary
                n = db.execute(
                    f"SELECT length(geoid20) FROM {acs_path.stem[3:]} LIMIT 1"
                ).fetchone()[0]
                if n == sql.GEOID_LEN[geog] - 1:
                    db.execute(
                        f"UPDATE {acs_path.stem[3:]} SET geoid20 = '0' || geoid20"
                    )

        if do_import:
            self.progress(msg=f"Adding CVAP data for {geog}...")
            with spatialite_connect(self.gpkg_path) as db:
                s = sql.add_cvap_fields.format(
                    table=geog, dec_yyyy=dec_year, dec_yy=dec_yy, acs_yyyy=acs_year, acs_yy=acs_yy
                )
                db.executescript(s)

                s = (sql.insert_cvap_data if acs_path else sql.insert_cvap_data_agg) \
                    .format(
                        table=geog, src_table=cvap_src_table, dec_yyyy=dec_year, dec_yy=dec_yy, acs_yyyy=acs_year, acs_yy=acs_yy, geoid="geoid20"
                )
                db.executescript(s)

            return True

        return False

    def import_decennial(self, dec_year='2020', acs_year='2021', vr_date=None):
        for geog in sql.PL_TABLES:
            self.progress(msg=f"Importing {geog}...")
            if not self.import_pl_geog(geog, dec_year):
                continue

            self.import_cvap_geog(geog, dec_year, acs_year)

            if geog == "block":
                if vr_date:
                    self.add_vr_to_block(geog, vr_date, dec_year)

    def cleanup(self):
        with spatialite_connect(self.gpkg_path) as db:
            for t in self.src_tables:
                db.execute(f"SELECT DropTable(NULL, '{t}')")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()
        return False
