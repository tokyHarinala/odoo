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
    'name': 'WISO-wso_product_purchase_history',
    'version': '1.0',
    'category': '',
    'description': """Product purchase and price history """,
    'description': """
Historique des achats
=============================
Cette module ajoute un onglet dans le fiche produit pour historiser les variations des prix
d'achat d'un article. Un champ qui garde en base le dernier prix d'achat permet de valoriser le stock
par rapport au prix du marché
""",
    'author': 'Wiso Consulting (tokyharinala@gmail.com)',
    'website': '',
    'license': 'AGPL-3',
    'depends': ['purchase'],
    'data':['security/ir.model.access.csv'],
    "category" : "Product Management",
    'init_xml': [],
    'update_xml': [
        'product_view.xml'
    ],
    'demo_xml': [],
    'active': False,
    'installable': True,
}

