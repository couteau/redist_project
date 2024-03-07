"""QGIS Redistricting Project Plugin - project builder

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
import json
import pathlib
from typing import Optional

from osgeo import ogr
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsVectorLayer,
    QgsVectorTileLayer
)
from qgis.PyQt.QtCore import QDirIterator
from redistricting.core import PlanBuilder

from ..datapkg.geography import Geography
from .fields import all_fields
from .settings import settings
from .state import State
from .utils import tr


def load_styles():
    styles = []
    it = QDirIterator(":/plugins/redist_project/style")
    while it.hasNext():
        styles.append(pathlib.Path(it.next()).stem)
    return styles


subdiv_geographies = {
    'place': ['b', 'bg', 't', 'vtd'],
    'cousub': ['b', 'bg', 't', 'vtd'],
    'concity': ['b', 'bg', 't', 'vtd'],
    'aiannh': ['b', 'bg', 't', 'vtd'],
    'county': ['b', 'bg', 't', 'vtd']
}


def add_base_map(project: QgsProject):
    mapUrl = "https://www.qwant.com/maps/tiles/ozbasemap/{z}/{x}/{y}.pbf"
    styleUrl = "https://raw.githubusercontent.com/QwantResearch/qwant-basic-gl-style/master/style.json"
    zmin = 0
    zmax = 14
    uri = f"styleUrl={styleUrl}&type=xyz&url={mapUrl}&zmin={zmin}&zmax={zmax}"
    tc = project.transformContext()
    tc.addCoordinateOperation(
        QgsCoordinateReferenceSystem("EPSG:3857"),
        project.crs(),
        "+proj=pipeline +step +inv +proj=webmerc +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +step "
        "+proj=unitconvert +xy_in=rad +xy_out=deg",
        True
    )
    project.setTransformContext(tc)
    lyr = QgsVectorTileLayer(uri, "Qwant")
    lyr.loadDefaultStyle()
    lyr.setOpacity(0.5)
    project.addMapLayer(lyr)


def create_plan_template(
    state: State,
    blocks: QgsVectorLayer,
    geogs: list[Geography],
    deviation: float,
    numdistricts: int,
    numseats: int,
    include_vap: bool,
    include_cvap: bool,
    include_vr: bool,
    fields: list[str]
):
    builder = PlanBuilder() \
        .setName("[template]") \
        .setGeoLayer(blocks) \
        .setDeviation(deviation) \
        .setNumSeats(numseats) \
        .setNumDistricts(numdistricts) \
        .setGeoIdField("geoid") \
        .setGeoDisplay(tr("Census Block")) \
        .setPopField("pop_total")

    if include_vap:
        builder.appendPopField("vap_total", caption=tr("Total VAP"))
    else:
        fields = [f for f in fields if all_fields[f]["pctbase"] != "vap_total"]

    if include_cvap:
        builder.appendPopField("cvap_total", caption=tr("Total CVAP"))
    else:
        fields = [f for f in fields if all_fields[f]["pctbase"] != "cvap_total"]

    if include_vr:
        builder.appendPopField("reg_total", caption=tr("Total Reg."))
    else:
        fields = [f for f in fields if all_fields[f]["pctbase"] != "reg_total"]

    for geog in geogs:
        if state.id == "la" and geog.geog == "c":
            caption = tr("Parish")
        else:
            caption = tr(geog.descrip)
        builder.appendGeoField(f"{geog.name}id", caption=caption)

    for f in fields:
        fld = all_fields[f]
        builder.appendDataField(f, caption=fld["caption"], sumfield=fld["sum"], pctbase=fld["pctbase"])

    return builder.createPlan(parent=QgsProject.instance(), createLayers=False)


def build_project(
        state: State,
        numdistricts: int,
        numseats: int = 0,
        deviation: float = 0,
        include_vap: bool = False,
        include_cvap: bool = False,
        include_vr: bool = False,
        geogs: dict[str, Geography] = None,
        subdiv_geog: Optional[str] = None,
        subdiv_id: Optional[str] = None,
        fields: Optional[list[str]] = None,
        base_map: Optional[bool] = False
):
    project = QgsProject.instance()
    crs = QgsCoordinateReferenceSystem("EPSG:4269")
    project.setCrs(crs)
    settings.iface.mapCanvas().setDestinationCrs(crs)

    if geogs is None:
        geogs = state.get_geographies()

    if subdiv_geog is not None:
        if subdiv_geog in subdiv_geographies:
            geogs = {g: geogs[g] for g in geogs if g in subdiv_geographies[subdiv_geog]}
            subdiv_idfield = f"{subdiv_geog}id"
            subset_str = f"{subdiv_idfield} = '{subdiv_id}'"
            subdiv_lyrname = f"{subdiv_geog}{state.year[-2:]}"
            subdiv_layer = QgsVectorLayer(f"{state.gpkg}|layername={subdiv_lyrname}", subdiv_lyrname, "ogr")
            feat = next(subdiv_layer.getFeatures(f"geoid = '{subdiv_id}'"))
            if not feat:
                subdiv_geog = None
            else:
                geom = feat.geometry().asWkt()

            subdiv_layer.setSubsetString(f"geoid = '{subdiv_id}'")
        else:
            subdiv_geog = None

    styles = load_styles()

    blocks = None
    layers = []
    plan_geogs = []
    for geog in geogs.values():
        lyrname = f"{geog.name}{state.year[-2:]}"
        lyr: QgsVectorLayer = QgsVectorLayer(f"{state.gpkg}|layername={lyrname}", lyrname, "ogr")
        if subdiv_geog is not None:
            if lyr.fields().lookupField(subdiv_idfield) != -1:
                lyr.setSubsetString(subset_str)
            else:
                n: ogr.DataSource = ogr.Open(str(state.gpkg), False)
                l: ogr.Layer = n.GetLayerByName(lyrname)
                m = ogr.CreateGeometryFromWkt(geom)
                l.SetSpatialFilter(m)
                ids = [str(f.GetFID()) for f in l]
                lyr.setSubsetString(f"fid in ({','.join(ids)})")

        project.addMapLayer(lyr)
        layers.append(lyr)
        if geog.geog == "b":
            blocks = lyr
        else:
            plan_geogs.append(geog.geog)
        if geog.name in styles:
            lyr.loadNamedStyle(f":/plugins/redist_project/style/{geog.name}.qml")

    if subdiv_geog is not None:
        project.addMapLayer(subdiv_layer)
        layers.append(subdiv_layer)
        subdiv_layer.loadNamedStyle(":/plugins/redist_project/style/county.qml")
        subdiv_layer.setLabelsEnabled(False)

    for rel in project.relationManager().discoverRelations([], layers):
        project.relationManager().addRelation(rel)

    if base_map:
        add_base_map(project)

    plan = create_plan_template(
        state,
        blocks,
        [geogs[g] for g in plan_geogs],
        deviation,
        numdistricts,
        numseats,
        include_vap,
        include_cvap,
        include_vr,
        fields
    )

    s = json.dumps(plan.serialize())

    project.writeEntry('redistricting', 'us-state', state.id)
    project.writeEntry('redistricting', 'us-decennial', state.year)
    project.writeEntry("redistricting", "us-template", s)

    return project
