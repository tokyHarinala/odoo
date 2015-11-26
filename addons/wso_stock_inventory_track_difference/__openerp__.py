# -*- coding: utf-8 -*-
##############################################################################
#
#    Module written to odoo for Warehouse management
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{   'name': 'wso_stock_inventory_track_difference',
    'version': '1.0',
    'description': """
Warehouse management and stock inventory
==============================================================
 Tableaux de bord de suivi des écarts d'inventaire par mois

    """,
    'category': 'Warehouse Management',
    'author': 'Wiso Consulting (tokyharinala@gmail.com)',
    'depends': [
        'stock'],
    'init_xml': [],
    'data': [
        'stock_difference.xml',
        ],
    'demo_xml': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
