
import requests
from bs4 import BeautifulSoup
from qgis.core import (
    Qgis,
    QgsMessageLog
)
from qgis.gui import QgisInterface
from qgis.utils import iface
from redistricting.utils import spatialite_connect

iface: QgisInterface


def cvap_years(year):
    # census ftp is too unreliable, so scrape available cvap years from html
    url = "https://www2.census.gov/programs-surveys/decennial/rdo/datasets"
    r = requests.get(url, allow_redirects=True, timeout=10)
    if not r.ok:
        QgsMessageLog.logMessage("Could not retrieve CVAP data", "Warning", Qgis.Warning)
        iface.messageBar().pushWarning("Warning", "Could not retrieve CVAP data")

    years = {}
    s = BeautifulSoup(r.content)
    table = s.find("table")  # the table element is
    contents = [row.find_all("td")[1].get_text()[:-1] for row in table.find_all("tr")[3:-1]]

    for y in contents:
        if int(y) >= int(year):
            years[y] = f"{url}/{y}/{y}-cvap/CVAP_{int(y)-4}-{y}_csv_files.zip"

    return years


__all__ = ["cvap_years", "spatialite_connect"]
