from dataclasses import dataclass


@dataclass
class Geography:
    geog: str
    name: str
    shp: str
    level: str


geographies = {
    "b": Geography(geog="b", name="block", shp="tabblock", level="750"),
    "vtd": Geography(geog="vtd", name="vtd", shp="vtd", level="700"),
    "t": Geography(geog="t", name="tract", shp="tract", level="140"),
    "c": Geography(geog="c", name="county", shp="county", level="050"),
    "p": Geography(geog="p", name="place", shp="place", level="160"),
    "aiannh": Geography(geog="aiannh", name="aiannh", shp="aiannh", level="280"),
    "bg": Geography(geog="bg", name="block group", shp="bg", level="150"),
    "cousub": Geography(geog="cousub", name="cousub", shp="cousub", level="060"),
    "st": Geography(geog="st", name="state", shp="state{", level="040")
}
