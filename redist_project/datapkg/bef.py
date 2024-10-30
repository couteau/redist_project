"""QGIS Redistricting Project Plugin - import block equivalency file

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
import csv
import pathlib
from collections.abc import Callable
from dataclasses import (
    dataclass,
    field
)
from typing import Union

import pandas as pd

from .geography import geographies
from .utils import (
    batched,
    spatialite_connect
)


@dataclass
class EquivalencyData:
    # for csvs without a header, col names will be strings of numeric indexes
    filepath: pathlib.Path
    joinField: str
    addFields: Union[dict[str, str], dict[int, str]] = field(default_factory=dict)


def import_equivalency(
    gpkg: pathlib.Path,
    geog: str,
    dec_year: str,
    bef: EquivalencyData,
    progress: Callable[[float], None] = None
):
    bef_file = pathlib.Path(bef.filepath).resolve()
    if not bef_file.exists() or not bef_file.is_file():
        return False

    with bef_file.open("rt", encoding="utf-8") as f:
        has_header = csv.Sniffer().has_header(f.read(4096))

    df = pd.read_csv(
        bef_file,
        index_col=bef.joinField,
        usecols=[bef.joinField, *bef.addFields.keys()],
        header=None if not has_header else "infer"
    ).rename(columns=bef.addFields)

    with spatialite_connect(gpkg) as db:
        table = f'{geographies[geog].name}{dec_year[-2:]}'
        sql = ";".join(f"ALTER TABLE {table} ADD COLUMN {c} TEXT" for c in df.columns) + ";"

        db.executescript(sql)

        sql = f"UPDATE {table} " \
            f"SET {', '.join(f'{f} = ?{n+2}' for n, f in enumerate(df.columns))} " \
            "WHERE geoid = ?1"

        total = len(df)
        count = 0
        for chunk in batched(df.itertuples(), total // 9 if total % 9 != 0 else total // 10):
            db.executemany(sql, chunk)
            count += len(chunk)
            if progress:
                progress(100 * count / total)

    return True
