"""QGIS Redistricting Project Plugin - import shapefile

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
from typing import (
    Callable,
    Union
)

from osgeo import (
    gdal,
    ogr
)


def import_shape(
    gpkg_path: Union[str, pathlib.Path],
    shp_path: Union[str, pathlib.Path],
    layer_name: str = None,
    filt=None,
    progress: Callable[[float], None] = None  # pylint: disable=deprecated-typing-alias
):
    gdal.UseExceptions()
    if isinstance(gpkg_path, str):
        gpkg_path = pathlib.Path(gpkg_path)

    if isinstance(shp_path, str):
        shp_path = pathlib.Path(shp_path)

    layer_name = layer_name or shp_path.stem

    src_ds: ogr.DataSource = ogr.Open(str(shp_path), False)
    if src_ds is None:
        print(
            f"Unable to open datasource `{shp_path:s}'."
        )
        return None

    src_layer: ogr.Layer = src_ds.GetLayer()
    if src_layer is None:
        print("FAILURE: Couldn't fetch layer!")
        return None

    dest_ds: ogr.DataSource = None
    with ogr.ExceptionMgr(useExceptions=False), gdal.quiet_errors():
        dest_ds: ogr.DataSource = ogr.Open(str(gpkg_path), True)

    if dest_ds is None:
        raise ValueError(f"Cannot open {gpkg_path}")

    if filt is not None:
        if src_layer.SetAttributeFilter(filt) != 0:
            print(f"FAILURE: SetAttributeFilter({filt}) failed.")
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
        layer_name, dest_crs, src_layer.GetGeomType(),
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
                if progress:
                    progress(100 * count / total)
        else:
            if progress:
                progress(100 * count / total)

    if chunk_size:
        dest_layer.CommitTransaction()
        progress(100 * count / total)

    dest_ds.Destroy()
    src_ds.Destroy()

    return result
