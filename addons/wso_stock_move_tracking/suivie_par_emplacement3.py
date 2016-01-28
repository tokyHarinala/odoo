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


class stock_inventory_per_location_temp(osv.osv_memory):
    _inherit = "stock.inventory.location.temp"


    def action_count_move(self, cr, uid, ids, process=None, my_date=None, context=None):
        res={}
        if not process:
            process='init'
        if type(ids) in (int, long,):
            ids= [ids]
        current_stock_inventory= self.browse(cr, uid, ids[0], context=context)
        if not my_date:
            my_date= datetime.datetime.strftime(datetime.datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)

        dom=[('state','=','done'),
            ('date','<',my_date),
            ('location_id','=',current_stock_inventory.emplacement_id.id),]
        inv_ids = self.pool.get('stock.inventory').search(cr, uid, dom, order="date desc", context=context)
        if inv_ids and inv_ids[0]:
            my_inv= self.pool.get('stock.inventory').browse(cr, uid, inv_ids[0])
            res={'inventory': my_inv}
        return res




    def action_get_stock_move_difference3(self, cr, uid, ids, in_date=None, to_date=None, location_id=None,context=None):
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

    def fill_init_inventory_product3(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        inventory_line_obj = self.pool.get('stock.inventory.location.lines.temp')

        if ids and len(ids):
            cr.execute('delete from stock_inventory_location_lines_temp where parent_id=%s', (ids[0],))
            self.write(cr, uid,ids,{'inventory_base_id': None})
            current_inv= self.browse(cr, uid, ids[0], context=context)
            process='init'
            basic_from_date= datetime.datetime.strptime(current_inv.from_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
            my_date_obj= datetime.datetime.combine(basic_from_date, datetime.datetime.min.time())
            my_date= datetime.datetime.strftime(my_date_obj, DEFAULT_SERVER_DATETIME_FORMAT)

            count_move_inv=self.action_count_move(cr, uid, ids, process, my_date, context)

            if count_move_inv and count_move_inv.get('inventory'):
                my_inventory= count_move_inv.get('inventory')
                self.write(cr, uid,ids,{'inventory_base_id': my_inventory.id})
                move_diff= self.action_get_stock_move_difference3(cr, uid, ids, my_inventory.date, my_date, current_inv.emplacement_id.id, context=context)
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
                    product = self.pool.get('product.product').browse(cr, uid, key, context=context)

                    if list_to_add_init.get(key)==0:
                        continue
                    inventory_line_obj.create(cr, uid,{
                                                        'product_id': key,
                                                        'beginning_qty': list_to_add_init.get(key),
                                                        'product_uom': product.uom_id.id,
                                                        'parent_id': ids[0],
                                                        }, context=context)

            else:
                self.fill_init_inventory_product2(cr, uid, ids, context=context)

        return True


    def fill_final_inventory_product3(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        inventory_line_obj = self.pool.get('stock.inventory.location.lines.temp')

        if ids and len(ids):
            current_inv= self.browse(cr, uid, ids[0], context=context)
            process='final'

            basic_to_date= datetime.datetime.strptime(current_inv.to_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
            my_date_obj= datetime.datetime.combine(basic_to_date, datetime.datetime.min.time()) + datetime.timedelta(days=1)
            my_date= datetime.datetime.strftime(my_date_obj, DEFAULT_SERVER_DATETIME_FORMAT)

            count_move_inv=self.action_count_move(cr, uid, ids, process, my_date, context)

            if count_move_inv and count_move_inv.get('inventory'):
                my_inventory= count_move_inv.get('inventory')
                move_diff= self.action_get_stock_move_difference3(cr, uid, ids, my_inventory.date, my_date, current_inv.emplacement_id.id, context=context)
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
                if current_inv.child_ids:
                    for line in current_inv.child_ids:
                        products.append(line.product_id.id)

                for key in list_to_add_final.keys():
                    if key in products:
                        line_ids= inventory_line_obj.search(cr, uid, [('product_id','=', key), ('parent_id','=', ids[0])], context=context)
                        for line_id in line_ids:
                            final_qty= inventory_line_obj.browse(cr,uid, line_id).final_qty + list_to_add_final.get(key)
                            inventory_line_obj.write(cr, uid, [line_id], {'final_qty': final_qty}, context= context)
                    else:
                        if list_to_add_final.get(key):
                            product = self.pool.get('product.product').browse(cr, uid, key, context=context)
                            inventory_line_obj.create(cr, uid,{
                                                        'product_id': key,
                                                        'final_qty': list_to_add_final.get(key),
                                                        'product_uom': product.uom_id.id,
                                                        'parent_id': ids[0],
                                                        }, context=context)

            else:
                self.fill_final_inventory_product2(cr, uid, ids, context=context)

        return True



    def make_inventory_temp3(self, cr, uid, ids, context):
        if ids and len(ids):
            self.fill_init_inventory_product3(cr, uid, ids, context=context)
            self.get_move_inventory_temp(cr, uid, ids, context=context)
            self.fill_final_inventory_product3(cr, uid, ids, context=context)

        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
             }

