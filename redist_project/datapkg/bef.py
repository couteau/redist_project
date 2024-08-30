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
from dataclasses import (
    dataclass,
    field
)
from itertools import islice
from typing import (
    Callable,
    Iterable,
    Union
)

import pandas as pd

from .utils import spatialite_connect


@dataclass
class BEFData:
    # for csvs without a header, col names will be strings of numeric indexes
    filepath: pathlib.Path
    joinField: str
    addFields: Union[dict[str, str], dict[int, str]] = field(default_factory=dict)


def add_bef_to_block(gpkg, dec_year, bef: BEFData, progress: Callable[[float], None]):  # pylint: disable=deprecated-typing-alias
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
    )
    df.rename(columns=bef.addFields, inplace=True)

    with spatialite_connect(gpkg) as db:
        sql = ";".join(f"ALTER TABLE block{dec_year[-2:]} ADD COLUMN {c} TEXT" for c in df.columns) + ";"

        db.executescript(sql)

        sql = f"UPDATE block{dec_year[-2:]} " \
            f"SET {', '.join(f'{f} = ?{n+2}' for n, f in enumerate(df.columns))} " \
            "WHERE geoid = ?1"

        total = len(df)
        count = 0
        records: Iterable[tuple] = df.itertuples()  # pylint: disable=deprecated-typing-alias
        chunk_size = total // 9
        last_chunk = total % 9
        for _ in range(9):
            f = islice(records, chunk_size)
            db.executemany(sql, f)
            count += chunk_size
            if progress:
                progress(100 * count / total)
        if last_chunk:
            f = islice(records, last_chunk)
            db.executemany(sql, f)
            count += last_chunk
        if progress:
            progress(100 * count / total)

    return True
