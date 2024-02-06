import ftplib

from redistricting.core.utils import spatialite_connect


def cvap_years(year):
    host = "ftp2.census.gov"
    folder = "/programs-surveys/decennial/rdo/datasets"

    ftp = ftplib.FTP(host, user="anonymous", passwd="")
    contents = ftp.nlst(folder)
    years = {}
    for f in contents:
        if "." not in f:
            y = f.rsplit("/", maxsplit=1)[1]
            if int(y) >= int(year):
                years[y] = f"{f}/{y}-cvap/CVAP_{int(y)-4}-{y}_csv_files.zip"

    return years


__all__ = ["cvap_years", "spatialite_connect"]
