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
'''
Created on 23 sept. 2015

@author: Toky
'''


from openerp.osv import fields, osv
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import openerp


class stock_suivi(osv.osv):
    _name = "stock.move.suivi"
    _description = "Products by Location"
    _columns = {
        'name': fields.related('product_id', 'name_template', type='char', relation='product.product', string='Libelle'),
        'all_product': fields.boolean('Tous les Articles'),
        'product_id': fields.many2one('product.product', 'Article'),
        'emplacement_id': fields.many2one('stock.location', 'Emplacement'),
        'from_date': fields.datetime('DU'),
        'to_date': fields.datetime('AU'),
        'type_suivi':fields.selection([
                            ('all','Tous'),
                            ('in','Entree'),
                            ('out','Sortie')], 'Type'),
        'state':fields.selection([
                            ('all','Tous'),
                            ('done', 'Terminer'),
                            ('waiting', 'En Attente'),
                            ('cancel', 'Cancelled'),
                            ('confirmed', 'En attente de disponibilite'),
                            ('assigned', 'Assigner')], 'Status'),
        'move_ids': fields.one2many('stock.move', 'suivi_id', 'Mouvement de stock')
        }
    _defaults = {
        'type_suivi': 'all',
        'state': 'all'
    }


    def create(self, cr, user, vals, context=None):
        vals2= vals.copy()
        if 'all_product' in vals.keys() and vals.get('all_product'):
            vals2['name']= 'Tous les Articles'
        elif not 'product_id' in vals.keys() or not vals.get('product_id'):
            raise openerp.exceptions.Warning("Veuillez specifier un article à suivre ou cocher la cage Tous les articles" )

        return super(stock_suivi, self).create(cr, user, vals2, context=context)

    def compute_move(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')

        if ids and len(ids):
            move_ids=[]
            nbr= self.search_count(cr, uid, [], context=context)
            if nbr>10:
                cr.execute('delete from stock_move_suivi where id!=%s', (ids[0],))
            current_suivi= self.browse(cr, uid, ids[0], context=context)
            location= current_suivi.emplacement_id
            type_suivi= current_suivi.type_suivi
            state= current_suivi.state
            from_date= False
            dt1= False
            domain=[]
            if current_suivi.from_date:
                basic_from_date= datetime.datetime.strptime(current_suivi.from_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
                from_date= datetime.datetime.strftime(basic_from_date, DEFAULT_SERVER_DATETIME_FORMAT)
            if current_suivi.to_date:
                basic_to_date= datetime.datetime.strptime(current_suivi.to_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
                obj_dt1= datetime.datetime.combine(basic_to_date, datetime.datetime.min.time()) + datetime.timedelta(days=1) - datetime.timedelta(minutes = 1)
                dt1= datetime.datetime.strftime(obj_dt1, DEFAULT_SERVER_DATETIME_FORMAT)

            if type_suivi=='all':
                if state=='all':
                    if not current_suivi.all_product:
                        domain+= [('product_id','=',current_suivi.product_id.id)]
                    if location:
                        domain+=['|',('location_dest_id','=',location.id),('location_id','=',location.id)]
                    if from_date:
                        domain.append(('date','>=' , from_date))
                    if dt1:
                        domain.append(('date','<=',dt1))
                    move_ids = move_obj.search(cr, uid, domain, context=context)
                else:
                    domain+= [('state','=',state)]
                    if not current_suivi.all_product:
                        domain+= [('product_id','=',current_suivi.product_id.id)]
                    if location:
                        domain+=['|',('location_dest_id','=',location.id),('location_id','=',location.id)]
                    if from_date:
                        domain.append(('date','>=' , from_date))
                    if dt1:
                        domain.append(('date','<=',dt1))
                    move_ids = move_obj.search(cr, uid, domain, context=context)

            if type_suivi=='in':
                if state=='all':
                    if not current_suivi.all_product:
                        domain+= [('product_id','=',current_suivi.product_id.id)]
                    if location:
                        domain+=[('location_dest_id','=',location.id)]
                    if from_date:
                        domain.append(('date','>=' , from_date))
                    if dt1:
                        domain.append(('date','<=',dt1))
                    move_ids = move_obj.search(cr, uid, domain, context=context)
                else:
                    domain+= [('state','=',state)]
                    if not current_suivi.all_product:
                        domain+= [('product_id','=',current_suivi.product_id.id)]
                    if location:
                        domain+=[('location_dest_id','=',location.id)]
                    if from_date:
                        domain.append(('date','>=' , from_date))
                    if dt1:
                        domain.append(('date','<=',dt1))
                    move_ids = move_obj.search(cr, uid, domain, context=context)

            if type_suivi=='out':
                if state=='all':
                    if not current_suivi.all_product:
                        domain+= [('product_id','=',current_suivi.product_id.id)]
                    if location:
                        domain+=[('location_id','=',location.id)]
                    if from_date:
                        domain.append(('date','>=' , from_date))
                    if dt1:
                        domain.append(('date','<=',dt1))
                    move_ids = move_obj.search(cr, uid, domain, context=context)
                else:
                    domain+= [('state','=',state)]
                    if not current_suivi.all_product:
                        domain+= [('product_id','=',current_suivi.product_id.id)]
                    if location:
                        domain+=[('location_id','=',location.id)]
                    if from_date:
                        domain.append(('date','>=' , from_date))
                    if dt1:
                        domain.append(('date','<=',dt1))
                    move_ids = move_obj.search(cr, uid, domain, context=context)


            self.write(cr, uid, current_suivi.id, {'move_ids': [(6, 0, move_ids)]}, context=context) # replace the list of linked IDs for each ID in the list of IDs)




        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
             }


stock_suivi()

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _description = "Internal Picking List"


    _columns = {
        'picking_in_number': fields.char('Num Livraison Fournisseur', size=64, help="La reference de la livraison du fournisseur.",domain = [('picking_type_id.code','=','incoming')]),
    }

class stock_move(osv.osv):
    _inherit="stock.move"
    _columns = {
        'suivi_id': fields.many2one('stock.move.suivi', 'Suivi', ondelete='set null'),
        'picking_in_number': fields.related('picking_id', 'picking_in_number', type='char', string='Num Livraison Fournisseur'),
        }
stock_move()