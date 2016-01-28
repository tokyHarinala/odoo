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
Created on 15 juin 2015

@author: Toky
'''

import datetime
from openerp.osv import  osv, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class stock_valuation(osv.osv):
    _inherit = "stock.valuation.product"
    _columns = {
        'inventory_base_id': fields.many2one('stock.inventory', 'Inventaire de base'),
        }


    def action_count_move(self, cr, uid, ids, process=None, my_date=None, context=None):
        res={}
        if not process:
            process='init'
        if type(ids) in (int, long,):
            ids= [ids]
        current_stock_valuation= self.browse(cr, uid, ids[0], context=context)
        if not my_date:
            my_date= datetime.datetime.strftime(datetime.datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)

        dom=[('state','=','done'),
            ('date','<',my_date),
            ('location_id','=',current_stock_valuation.emplacement_id.id),]
        inv_ids = self.pool.get('stock.inventory').search(cr, uid, dom, order="date desc", context=context)
        if inv_ids and inv_ids[0]:
            my_inv= self.pool.get('stock.inventory').browse(cr, uid, inv_ids[0])
#             basic_date_inv= datetime.datetime.strptime(my_inv.date, DEFAULT_SERVER_DATETIME_FORMAT).date()
#             date_inv_obj= datetime.datetime.combine(basic_date_inv, datetime.datetime.min.time()) + datetime.timedelta(days=1)
#             date_inv= datetime.datetime.strftime(date_inv_obj, DEFAULT_SERVER_DATETIME_FORMAT)
#             cr.execute('SELECT count(id) FROM stock_move WHERE state=%s and  date>=%s and date< %s', ('done',date_inv,my_date,))
#             num_entry_inv = cr.fetchone()[0] or 0
#             cr.execute('SELECT count(id) FROM stock_move WHERE state=%s and date>%s', ('done',my_date,))
#             num_entry_quant = cr.fetchone()[0] or 0
#             if num_entry_inv < num_entry_quant:
#                 res={'inventory': my_inv}

            res={'inventory': my_inv}
        return res




    def action_get_stock_move_difference2(self, cr, uid, ids, in_date=None, to_date=None, location_id=None,context=None):
        move_list={}
        if type(ids) in (int, long,):
            ids= [ids]
        if not location_id:
            return {}
        stock_move=self.pool.get("stock.move")
        if not in_date:
            in_date= datetime.datetime.now()
        if not to_date:
            to_date= datetime.datetime.now()

        basic_in_date= datetime.datetime.strptime(in_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
        my_in_date_obj= datetime.datetime.combine(basic_in_date, datetime.datetime.min.time()) + datetime.timedelta(days=1)
        my_in_date= datetime.datetime.strftime(my_in_date_obj, DEFAULT_SERVER_DATETIME_FORMAT)

        dom=[('state','=','done'),
            ('date','>=',my_in_date),
            ('date','<',to_date),
            '|',('location_dest_id','=',location_id),('location_id','=',location_id)]
        move_ids = stock_move.search(cr, uid, dom, context=context)
        move_lines= stock_move.browse(cr, uid, move_ids)
        list_key=[]
        for move in move_lines:
            key=move.product_id.id
            if key in list_key:
                if move.location_id.id==location_id:
                    move_list[key]-= move.product_uom_qty
                else:
                    move_list[key]+= move.product_uom_qty
            else:
                move_list[key]=0
                if move.location_id.id==location_id:
                    move_list[key]-= move.product_uom_qty
                else:
                    move_list[key]+= move.product_uom_qty
                list_key.append(key)
        return move_list

    def fill_init_inventory_product2(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        valuation_line_obj = self.pool.get('stock.valuation.product.lines')

        if ids and len(ids):
            cr.execute('delete from stock_valuation_product_lines where parent_production_id=%s', (ids[0],))
            self.write(cr, uid,ids,{'inventory_base_id': None})
            current_valuation= self.browse(cr, uid, ids[0], context=context)
            type_valuation= current_valuation.type_valuation
            process='init'
            basic_from_date= datetime.datetime.strptime(current_valuation.from_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
            my_date_obj= datetime.datetime.combine(basic_from_date, datetime.datetime.min.time())
            my_date= datetime.datetime.strftime(my_date_obj, DEFAULT_SERVER_DATETIME_FORMAT)

            count_move_inv=self.action_count_move(cr, uid, ids, process, my_date, context)

            if count_move_inv and count_move_inv.get('inventory'):
                my_inventory= count_move_inv.get('inventory')
                self.write(cr, uid,ids,{'inventory_base_id': my_inventory.id})
                move_diff= self.action_get_stock_move_difference2(cr, uid, ids, my_inventory.date, my_date, current_valuation.emplacement_id.id, context=context)
                list_to_add_init={}
                for inv_line in my_inventory.line_ids:
                    if inv_line.product_id.id not in list_to_add_init.keys():
                        list_to_add_init[inv_line.product_id.id]= inv_line.product_qty
                    else:
                        list_to_add_init[inv_line.product_id.id]+= inv_line.product_qty
                for move_key in move_diff.keys():
                    if move_key not in list_to_add_init.keys():
                        list_to_add_init[move_key]= move_diff.get(move_key)
                    else:
                        list_to_add_init[move_key]+= move_diff.get(move_key)

                for key in list_to_add_init.keys():
                    if list_to_add_init.get(key)==0:
                        continue
                    product = self.pool.get('product.product').browse(cr, uid, key, context=context)
                    price_cump= product.standard_price or 0.0
                    last_purchase_price= product.last_purchase_price or 0.0

                    if type_valuation== 'last_purchase_price':
                        valuation= last_purchase_price * list_to_add_init.get(key)
                    else:
                        if price_cump==0 and last_purchase_price!=0:
                            price_cump= last_purchase_price
                        price= price_cump
#                         price= self.get_history_price(cr, uid, ids, key, current_valuation.from_date, context=context) or price_cump
                        valuation= price * list_to_add_init.get(key)
                    valuation_line_obj.create(cr, uid,{
                                                        'product_id': key,
                                                        'beginning_qty': list_to_add_init.get(key),
                                                        'beginning_valuation': valuation,
                                                        'product_uom': product.uom_id.id,
                                                        'parent_production_id': ids[0],
                                                        }, context=context)

            else:
                self.fill_init_valuation_product(cr, uid, ids, context=context)

        return True


    def fill_final_inventory_product2(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        valuation_line_obj = self.pool.get('stock.valuation.product.lines')

        if ids and len(ids):
            current_valuation= self.browse(cr, uid, ids[0], context=context)
            type_valuation= current_valuation.type_valuation
            process='final'

            basic_to_date= datetime.datetime.strptime(current_valuation.to_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
            my_date_obj= datetime.datetime.combine(basic_to_date, datetime.datetime.min.time()) + datetime.timedelta(days=1)
            my_date= datetime.datetime.strftime(my_date_obj, DEFAULT_SERVER_DATETIME_FORMAT)

            count_move_inv=self.action_count_move(cr, uid, ids, process, my_date, context)

            if count_move_inv and count_move_inv.get('inventory'):
                my_inventory= count_move_inv.get('inventory')
                move_diff= self.action_get_stock_move_difference2(cr, uid, ids, my_inventory.date, my_date, current_valuation.emplacement_id.id, context=context)
                list_to_add_final={}
                for inv_line in my_inventory.line_ids:
                    if inv_line.product_id.id not in list_to_add_final.keys():
                        list_to_add_final[inv_line.product_id.id]= inv_line.product_qty
                    else:
                        list_to_add_final[inv_line.product_id.id]+= inv_line.product_qty
                for move_key in move_diff.keys():
                    if move_key not in list_to_add_final.keys():
                        list_to_add_final[move_key]= move_diff.get(move_key)
                    else:
                        list_to_add_final[move_key]+= move_diff.get(move_key)

                products=[]
                if current_valuation.child_ids:
                    for line in current_valuation.child_ids:
                        products.append(line.product_id.id)

                for key in list_to_add_final.keys():
                    if key in products:
                        product = self.pool.get('product.product').browse(cr, uid, key, context=context)
                        price_cump= product.standard_price or 0.0
                        last_purchase_price= product.last_purchase_price or 0.0
                        line_ids= valuation_line_obj.search(cr, uid, [('product_id','=', key), ('parent_production_id','=', ids[0])], context=context)
                        for line_id in line_ids:
                            final_qty= valuation_line_obj.browse(cr,uid, line_id).final_qty + list_to_add_final.get(key)
                            if type_valuation== 'last_purchase_price':
                                valuation= last_purchase_price * final_qty
                            else:
                                if price_cump==0 and last_purchase_price!=0:
                                    price_cump= last_purchase_price
                                price2= price_cump
#                                 price2= self.get_history_price(cr, uid, ids, key, current_valuation.to_date, context=context) or price_cump
                                valuation= price2 * final_qty
                            valuation_line_obj.write(cr, uid, [line_id], {'final_qty': final_qty,'final_valuation':valuation}, context= context)
                    else:
                        if list_to_add_final.get(key):
                            if list_to_add_final.get(key)==0:
                                continue
                            product = self.pool.get('product.product').browse(cr, uid, key, context=context)
                            price_cump= product.standard_price or 0.0
                            last_purchase_price= product.last_purchase_price or 0.0

                            if type_valuation== 'last_purchase_price':
                                valuation= last_purchase_price * list_to_add_final.get(key)
                            else:
                                if price_cump==0 and last_purchase_price!=0:
                                    price_cump= last_purchase_price
                                price2= price_cump
#                                 price2= self.get_history_price(cr, uid, ids, key, current_valuation.to_date, context=context) or price_cump
                                valuation= price2 * list_to_add_final.get(key)
                            valuation_line_obj.create(cr, uid,{
                                                        'product_id': key,
                                                        'final_qty': list_to_add_final.get(key),
                                                        'final_valuation': valuation,
                                                        'product_uom': product.uom_id.id,
                                                        'parent_production_id': ids[0],
                                                        }, context=context)

            else:
                self.fill_final_valuation_product(cr, uid, ids, context=context)

        return True



    def make_valuation2(self, cr, uid, ids, context):
        if ids and len(ids):
            self.fill_init_inventory_product2(cr, uid, ids, context=context)
            self.get_move_valuation(cr, uid, ids, context=context)
            self.fill_final_inventory_product2(cr, uid, ids, context=context)

        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
             }

