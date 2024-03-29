# -*- coding: utf-8 -*-
"""US Census Data for QGIS Qedistricting Plugin

        begin                : 2024-01-20
        copyright            : (C) 2024 by Cryptodira
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
from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    """Census identifiers for each state"""
    state: str
    fips: str
    ns: str
    name: str


states = {
    'al': State(state='al', fips='01', ns='01779775', name='Alabama'),
    'ak': State(state='ak', fips='02', ns='01785533', name='Alaska'),
    'az': State(state='az', fips='04', ns='01779777', name='Arizona'),
    'ar': State(state='ar', fips='05', ns='00068085', name='Arkansas'),
    'ca': State(state='ca', fips='06', ns='01779778', name='California'),
    'co': State(state='co', fips='08', ns='01779779', name='Colorado'),
    'ct': State(state='ct', fips='09', ns='01779780', name='Connecticut'),
    'de': State(state='de', fips='10', ns='01779781', name='Delaware'),
    'dc': State(state='dc', fips='11', ns='01702382', name='District of Columbia'),
    'fl': State(state='fl', fips='12', ns='00294478', name='Florida'),
    'ga': State(state='ga', fips='13', ns='01705317', name='Georgia'),
    'hi': State(state='hi', fips='15', ns='01779782', name='Hawaii'),
    'id': State(state='id', fips='16', ns='01779783', name='Idaho'),
    'il': State(state='il', fips='17', ns='01779784', name='Illinois'),
    'in': State(state='in', fips='18', ns='00448508', name='Indiana'),
    'ia': State(state='ia', fips='19', ns='01779785', name='Iowa'),
    'ks': State(state='ks', fips='20', ns='00481813', name='Kansas'),
    'ky': State(state='ky', fips='21', ns='01779786', name='Kentucky'),
    'la': State(state='la', fips='22', ns='01629543', name='Louisiana'),
    'me': State(state='me', fips='23', ns='01779787', name='Maine'),
    'md': State(state='md', fips='24', ns='01714934', name='Maryland'),
    'ma': State(state='ma', fips='25', ns='00606926', name='Massachusetts'),
    'mi': State(state='mi', fips='26', ns='01779789', name='Michigan'),
    'mn': State(state='mn', fips='27', ns='00662849', name='Minnesota'),
    'ms': State(state='ms', fips='28', ns='01779790', name='Mississippi'),
    'mo': State(state='mo', fips='29', ns='01779791', name='Missouri'),
    'mt': State(state='mt', fips='30', ns='00767982', name='Montana'),
    'ne': State(state='ne', fips='31', ns='01779792', name='Nebraska'),
    'nv': State(state='nv', fips='32', ns='01779793', name='Nevada'),
    'nh': State(state='nh', fips='33', ns='01779794', name='New Hampshire'),
    'nj': State(state='nj', fips='34', ns='01779795', name='New Jersey'),
    'nm': State(state='nm', fips='35', ns='00897535', name='New Mexico'),
    'ny': State(state='ny', fips='36', ns='01779796', name='New York'),
    'nc': State(state='nc', fips='37', ns='01027616', name='North Carolina'),
    'nd': State(state='nd', fips='38', ns='01779797', name='North Dakota'),
    'oh': State(state='oh', fips='39', ns='01085497', name='Ohio'),
    'ok': State(state='ok', fips='40', ns='01102857', name='Oklahoma'),
    'or': State(state='or', fips='41', ns='01155107', name='Oregon'),
    'pa': State(state='pa', fips='42', ns='01779798', name='Pennsylvania'),
    'ri': State(state='ri', fips='44', ns='01219835', name='Rhode Island'),
    'sc': State(state='sc', fips='45', ns='01779799', name='South Carolina'),
    'sd': State(state='sd', fips='46', ns='01785534', name='South Dakota'),
    'tn': State(state='tn', fips='47', ns='01325873', name='Tennessee'),
    'tx': State(state='tx', fips='48', ns='01779801', name='Texas'),
    'ut': State(state='ut', fips='49', ns='01455989', name='Utah'),
    'vt': State(state='vt', fips='50', ns='01779802', name='Vermont'),
    'va': State(state='va', fips='51', ns='01779803', name='Virginia'),
    'wa': State(state='wa', fips='53', ns='01779804', name='Washington'),
    'wv': State(state='wv', fips='54', ns='01779805', name='West Virginia'),
    'wi': State(state='wi', fips='55', ns='01779806', name='Wisconsin'),
    'wy': State(state='wy', fips='56', ns='01779807', name='Wyoming'),
    # 'as': State(state='as', fips='60', ns='01802701', name='American Samoa'),
    # 'gu': State(state='gu', fips='66', ns='01802705', name='Guam'),
    # 'mp': State(state='mp', fips='69', ns='01779809',
    #            name='Commonwealth of the Northern Mariana Islands'),
    'pr': State(state='pr', fips='72', ns='01779808', name='Puerto Rico'),
    # 'um': State(state='um', fips='74', ns='01878752', name='U.S. Minor Outlying Islands'),
    # 'vi': State(state='vi', fips='78', ns='01802710', name='United States Virgin Islands'),
}

__all_states = [
    'al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'dc', 'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia', 'ks',
    'ky', 'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj', 'nm', 'ny', 'nc',
    'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt', 'va', 'wa', 'wv', 'wi', 'wy', 'pr'
]
