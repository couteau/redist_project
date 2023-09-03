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
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

__author__ = "Stuart C. Naifeh"
__contact__ = "stuart@cryptodira.org"
__copyright__ = "Copyright (c) 2022, Stuart C. Naifeh"
__license__ = "GPLv3"
__version__ = "0.0.1"

# noinspection PyPep8Naming


def classFactory(iface):  # pylint: disable=invalid-name
    """Create an instance of the Redistricting plugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    # pylint: disable-next=import-outside-toplevel
    from .redist_project import RdProjectGenerator
    return RdProjectGenerator(iface)
