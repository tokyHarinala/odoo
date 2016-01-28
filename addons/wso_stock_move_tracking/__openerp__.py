# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

{
    'name': "wso_stock_move_tracking - Warehouse Management and stock inventory",
    'version': '1.0',
    'category': '"Warehouse Management"',
    'description': """
Suivi de stock par emplacement
==============================
Elle donne une vue globale de l'état de stock d'un emplacement pour une intervale de date bien définie:

    - Stock initial
    - Entrée
    - Sortie
    - Stock final

""",
    'author': 'Dzama Consulting (tokyharinala@gmail.com)',
    'website': 'http://www.dzama.mg',
    'license': 'AGPL-3',
    'depends': ['stock'],
    'init_xml': [],
    'data': [
             'suivie_par_emplacement_view.xml',
             'security/ir.model.access.csv',
             ],

    'demo_xml': [],
    'active': False,
    'installable': True,
}

