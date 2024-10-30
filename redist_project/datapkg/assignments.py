# -*- coding: utf-8 -*-
"""Redistricting Project Generator 

    Generate projects for the QGIS Redistricting Plugin 
    from standardized redistricting datasets

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
import pathlib

import pandas as pd

from .state import states

assignments = {
    'place': 'INCPLACE_CDP',
    'aiannh': 'AIANNH',
}


def join_assignments(st: str, dec_year: str, df: pd.DataFrame, src_path: pathlib.Path):  # pylint: disable=unused-argument
    """Join place and aiannh assignment file csvs

    Arguments:
        st {str} -- two-letter state code
        dec_year {str} -- four-digit decennial census year
        df {pd.DataFrame} -- dataframe to join assignments to
        src_path {pathlib.Path} -- path where assignment files are located

    Returns:
        pd.DataFrame -- the joined dataframe
    """
    baf = []
    for field in assignments.values():
        fn = f"BlockAssign_ST{states[st].fips}_{st.upper()}_{field}.txt"
        p = src_path / "baf" / fn
        baf.append(pd.read_csv(p, header=0, delimiter='|', index_col='BLOCKID'))

    return df.join(baf)
