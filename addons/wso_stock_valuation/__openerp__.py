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
    'name': 'WISO-wso_stock_valuation-Stock valuation',
    'version': '1.0',
    'category': '',
    'description': """
Valorisation de stock entre deux date
=====================================
Elle donne une accèss aux flux des mouvements par emplacement et sa valorisation

La valorisation peut être baser sur deux principes:
    - Valorisation par CUMP
    - Valorisation par le dernier prix d'achat

Le résultat affiche le couple quantité/valeurs du stock de l'emplacement concerné:
    - Quantité/valeur stock initial
    - Quantité/valeur Entrée
    - Quantité/valeur Sortie
    - Quantité/valeur stock final

""",
    'author': 'Wiso Consulting (tokyharinala@gmail.com)',
    'website': '',
    'license': 'AGPL-3',
    'depends': ['wso_product_purchase_history'],
    'data':['security/ir.model.access.csv'],
    "category" : "Warehouse Management",
    'init_xml': [],
    'update_xml': [
        'stock_valuation.xml'
    ],
    'demo_xml': [],
    'active': False,
    'installable': True,
}

