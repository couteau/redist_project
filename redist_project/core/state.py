# -*- coding: utf-8 -*-
"""QGIS Redistricting Project Plugin - state

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
import random
from dataclasses import dataclass
from typing import Optional

import pandas as pd
from qgis.PyQt.QtCore import QObject
from redistricting.utils import spatialite_connect

from ..datapkg.geography import (
    Geography,
    geographies
)
from ..datapkg.state import State as CensusState
from ..datapkg.state import states as census_states
from .settings import settings

geog_order = [

]


class State(QObject):
    def __init__(
        self,
        st: CensusState,
        year: str,
        gpkg_path: pathlib.Path = None,
        custom_id: Optional[str] = None,
        custom_name: str = ""
    ):
        super().__init__(None)
        self.st = st
        self.year = year
        if custom_id is not None and not custom_name:
            raise ValueError("Custom name must be provided for custom state packages")
        self.custom_id = custom_id
        self.custom_name = custom_name
        if gpkg_path is None:
            self.gpkg = settings.datapath / geopackage_name(self)
        else:
            self.gpkg = gpkg_path

    @classmethod
    def fromState(cls, state: 'State') -> 'State':
        custom_id = f"{random.randint(0, 0xffffff):06x}"
        return cls(state.st, state.year, custom_id=custom_id, custom_name=custom_id)

    def get_geographies(self) -> dict[str, Geography]:
        if not self.gpkg_exists():
            return {}

        with spatialite_connect(self.gpkg) as db:
            c = db.execute(
                f"select table_name from gpkg_contents where data_type = 'features' and table_name like '%{self.year[:-2]}'")
            geogs = [r[0][:-2] for r in c]

        return {g.geog: g for g in geographies.values() if g.name in geogs}

    def get_subdivisions(self, geog: str) -> list["Subdivision"]:
        if not self.gpkg_exists():
            return []

        with spatialite_connect(self.gpkg) as db:
            table = f"{geographies[geog].name}{self.year[-2:]}"
            c = db.execute(f"select geoid, name from {table}")

            return [Subdivision(state=self, geog=geographies[geog], geoid=g[0], name=g[1]) for g in c]

    def get_customshapes(self):
        with spatialite_connect(self.gpkg) as db:
            c = db.execute(
                f"select table_name from gpkg_contents where data_type = 'features' and table_name not like '%{self.year[:-2]}'"
            )
            return [r[0] for r in c]

    def gpkg_exists(self):
        return self.gpkg and self.gpkg.exists()

    def has_cvap(self):
        if not self.gpkg_exists():
            return False

        with spatialite_connect(self.gpkg) as db:
            schema = pd.read_sql_query(
                f"PRAGMA table_info('block{self.year[-2:]}')", db, index_col="name")
            return "cvap_total" in schema.index

    def has_vr(self):
        if not self.gpkg_exists():
            return False

        with spatialite_connect(self.gpkg) as db:
            schema = pd.read_sql_query(
                f"PRAGMA table_info('block{self.year[-2:]}')", db, index_col="name")
            return "reg_total" in schema.index

    @property
    def id(self):
        return self.code if self.custom_id is None else f"{self.code}@{self.custom_id}"

    @property
    def code(self):
        return self.st.state

    @property
    def name(self):
        return self.st.name

    @property
    def packageName(self):
        return self.name if self.custom_id is None else self.custom_name

    @property
    def fips(self):
        return self.st.fips

    @property
    def stusab(self):
        return self.st.state.upper()


class StateList:
    def __init__(self, dec_year, states=None):
        self.dec_year = dec_year
        if states is None:
            self.states = {s: State(st, dec_year)
                           for s, st in census_states.items()}
        else:
            self.states = {
                s: State(census_states[s], dec_year) for s in states}

        self.custom_pkgs = {}
        for s in settings.customPackages:
            st = State(
                census_states[s["st"]],
                year=s["dec_year"],
                gpkg_path=pathlib.Path(s["gpkg_path"]),
                custom_id=s["id"],
                custom_name=s["name"]
            )
            self.custom_pkgs[st.code] = st

        if self.custom_pkgs:
            self.sort_states()

    def __getitem__(self, __index) -> State:
        if isinstance(__index, str):
            return self.states[__index]

        if isinstance(__index, int):
            return list(self.states.values())[__index]

        if isinstance(__index, slice):
            states = list(census_states.keys())[__index]
            return StateList(self.dec_year, states)

        if isinstance(__index, tuple):
            if len(__index) != 2:
                raise IndexError("Invalid index")

            row = self[__index[0]]
            col = __index[1]
            if isinstance(col, str):
                return getattr(row, col) if isinstance(row, State) else [getattr(r, col) for r in row]

            if isinstance(col, int):
                columns = [key for key, value in State.__dict__.items(
                ) if isinstance(value, property)]
                if 0 <= col < len(columns):
                    return getattr(row, columns[col]) \
                        if isinstance(row, State) \
                        else [getattr(r, columns[col]) for r in row]

            raise IndexError(f"Invalid index {col}")

        raise IndexError("Invalid index")

    def __iter__(self):
        return (s for s in self.states.values())

    def index(self, state: State) -> int:
        return list(self.states.keys()).index(state.id)

    def row_count(self):
        return len(self.states)

    def col_count(self):
        return len([key for key, value in State.__dict__.items() if isinstance(value, property)])

    def sort_states(self):
        keys = {*self.states.keys(), *self.custom_pkgs.keys()}
        states = dict.fromkeys(sorted(keys))
        states.update(self.states)
        states.update(self.custom_pkgs)
        self.states = states

    def add_custom_package(self, state: State):
        self.custom_pkgs[state.id] = state
        self.sort_states()
        return state


@dataclass
class Subdivision:
    state: State
    geog: Geography
    geoid: str
    name: str


def geopackage_name(state: State):
    return f"{state.packageName.replace(' ', '_').lower()}.gpkg"
