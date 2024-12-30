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
import random
from dataclasses import dataclass

import pandas as pd
from redistricting.utils import spatialite_connect

from ..datapkg.geography import (
    Geography,
    geographies
)
from ..datapkg.state import State as CensusState
from ..datapkg.state import states as census_states
from .settings import settings


class State:
    def __init__(
        self,
        census_state: CensusState,
        year: str,
        package_id: str,
        package_name: str = None
    ):
        self.state = census_state
        self.year = year
        self.package_id = package_id
        self.package_name = package_name or census_state.name
        self.gpkg = settings.datapath / f'{package_id}.gpkg'

    @classmethod
    def fromState(cls, state: 'State') -> 'State':
        custom_id = f"{random.randint(0, 0xffffff):06x}"
        return cls(state.state, state.year, package_id=custom_id)

    def gpkg_exists(self):
        return self.gpkg.exists()

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
        return f"{self.code}@{self.package_id}"

    @property
    def code(self):
        return self.state.state

    @property
    def name(self):
        return self.state.name

    @property
    def fips(self):
        return self.state.fips

    @property
    def stusab(self):
        return self.state.state.upper()


class StateList:
    def __init__(self, dec_year, states=None):
        self.dec_year = dec_year
        if states is None:
            self._states = {s: State(st, dec_year, st.name) for s, st in census_states.items()}
        else:
            self._states = {s: State(census_states[s], dec_year, census_states[s]) for s in states}

        self.custom_pkgs = {}
        for s in settings.customPackages:
            st = State(
                census_states[s["st"]],
                year=s["dec_year"],
                package_id=s["id"],
                package_name=s["name"]
            )
            self.custom_pkgs[st.code] = st

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
        keys = {*self._states.keys(), *self.custom_pkgs.keys()}
        states = dict.fromkeys(sorted(keys))
        states.update(self._states)
        states.update(self.custom_pkgs)
        self.states = states

    def add_custom_package(self, state: State):
        self.custom_pkgs[state.id] = state
        self.sort_states()

        settings.addCustomPackage(
            state.state.state,
            state.id,
            state.year,
            state.package_name,
        )

        return state


@dataclass
class Subdivision:
    state: State
    geog: Geography
    geoid: str
    name: str


def geopackage_name(state: State):
    return f"{state.package_name.replace(' ', '_').lower()}.gpkg"
