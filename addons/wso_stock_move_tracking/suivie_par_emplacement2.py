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

from openerp.osv import fields, osv
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class stock_inventory_per_location_temp(osv.osv_memory):

    _name = "stock.inventory.location.temp"
    _description = "Products by Location"
    _columns = {
        'name': fields.related('emplacement_id', 'name', string="Nom", type='char'),
        'emplacement_id': fields.many2one('stock.location', 'Emplacement', required=True),
        'from_date': fields.datetime('DU'),
        'to_date': fields.datetime('AU'),
        'inventory_base_id': fields.many2one('stock.inventory', 'Inventaire de base'),
        'child_ids': fields.one2many('stock.inventory.location.lines.temp', 'parent_id', 'Articles')
        }


    def _get_inventory_lines(self, cr, uid, inventory, context=None):
        product_obj = self.pool.get('product.product')
        domain = ' location_id = %s'
        args = (inventory.emplacement_id.id,)

        cr.execute('''
           SELECT product_id, sum(qty) as product_qty, location_id
           FROM stock_quant WHERE''' + domain + '''
           GROUP BY product_id, location_id
        ''', args)
        vals = []
        for product_line in cr.dictfetchall():
            #replace the None the dictionary by False, because falsy values are tested later on
            for key, value in product_line.items():
                if not value:
                    product_line[key] = False
            product_line['parent_id'] = inventory.id
            product_line['product_qty']
            if product_line['product_id']:
                product = product_obj.browse(cr, uid, product_line['product_id'], context=context)
                product_line['product_uom'] = product.uom_id.id
            vals.append(product_line)
        return vals


    def action_get_stock_move_difference(self, cr, uid, ids, process='init',context=None):
        if type(ids) in (int, long,):
            ids= [ids]
        stock_move=self.pool.get("stock.move")
        current_stock_inventory= self.browse(cr, uid, ids[0], context=context)
        my_date_obj=datetime.datetime.now()
        if process=='init':
            basic_from_date= datetime.datetime.strptime(current_stock_inventory.from_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
            my_date_obj= datetime.datetime.combine(basic_from_date, datetime.datetime.min.time())
        else:
            basic_to_date= datetime.datetime.strptime(current_stock_inventory.to_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
            my_date_obj= datetime.datetime.combine(basic_to_date, datetime.datetime.min.time()) + datetime.timedelta(days=1)

        move_list={}
        if my_date_obj < datetime.datetime.now():
            my_date= datetime.datetime.strftime(my_date_obj, DEFAULT_SERVER_DATETIME_FORMAT)
            location_id= current_stock_inventory.emplacement_id.id
            dom=[('state','=','done'),
                 ('date','>=',my_date),
                 '|',('location_dest_id','=',location_id),('location_id','=',location_id)]
            move_ids = stock_move.search(cr, uid, dom, context=context)
            move_lines= stock_move.browse(cr, uid, move_ids)
            list_key=[]
            for move in move_lines:
                key=move.product_id.id
                if key in list_key:
                    if move.location_id.id==location_id:
                        move_list[key]+= move.product_uom_qty
                    else:
                        move_list[key]-= move.product_uom_qty
                else:
                    move_list[key]=0
                    if move.location_id.id==location_id:
                        move_list[key]+= move.product_uom_qty
                    else:
                        move_list[key]-= move.product_uom_qty
                    list_key.append(key)
        return move_list



    def fill_init_inventory_product2(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        inventory_line_obj = self.pool.get('stock.inventory.location.lines.temp')

        if ids and len(ids):
            cr.execute('delete from stock_inventory_location_lines_temp where parent_id=%s', (ids[0],))
            current_inv= self.browse(cr, uid, ids[0], context=context)
            process='init'
            vals = self._get_inventory_lines(cr, uid, current_inv, context=context)
            move_lines= self.action_get_stock_move_difference(cr, uid, ids, process, context=context)
            if move_lines:
                list_vals_keys=[val.get('product_id') for val in vals]
                for key in move_lines.keys():
                    if key in list_vals_keys:
                        for p_line in vals:
                            if p_line.get('product_id')==key:
                                p_line['product_qty']+= move_lines[key]
                    else:
                        product = self.pool.get('product.product').browse(cr, uid, key, context=context)
                        product_line={'product_id': key,
                                      'product_uom': product.uom_id.id,
                                      'product_qty': move_lines[key],
                                      'parent_id': current_inv.id
                                                    }
                        vals.append(product_line)
                        list_vals_keys.append(key)
            for product_line in vals:
                if product_line.get('product_qty')==0:
                    continue
                inventory_line_obj.create(cr, uid,{
                                                    'product_id': product_line.get('product_id'),
                                                    'beginning_qty': product_line.get('product_qty'),
                                                    'product_uom': product_line.get('product_uom'),
                                                    'parent_id': ids[0],
                                                    }, context=context)





    def fill_final_inventory_product2(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        inventory_line_obj = self.pool.get('stock.inventory.location.lines.temp')

        if ids and len(ids):
            current_inv= self.browse(cr, uid, ids[0], context=context)
            process='final'
            vals2 = self._get_inventory_lines(cr, uid, current_inv, context=context)
            move_lines= self.action_get_stock_move_difference(cr, uid, ids, process, context=context)
            if move_lines:
                list_vals_keys=[val.get('product_id') for val in vals2]
                for key2 in move_lines.keys():
                    if key2 in list_vals_keys:
                        for p_line in vals2:
                            if p_line.get('product_id')==key2:
                                p_line['product_qty']+= move_lines[key2]
                    else:
                        product = self.pool.get('product.product').browse(cr, uid, key2, context=context)
                        product_line2={'product_id': key2,
                                        'product_uom': product.uom_id.id,
                                        'product_qty': move_lines[key2],
                                        'parent_id': current_inv.id
                                                    }
                        vals2.append(product_line2)
                        list_vals_keys.append(key2)
            if current_inv.child_ids:
                products=[]
                for line in current_inv.child_ids:
                    products.append(line.product_id.id)
            for product_line2 in vals2:
                if product_line2.get('product_id') in products:
                    line_ids= inventory_line_obj.search(cr, uid, [('product_id','=', product_line2.get('product_id')), ('parent_id','=', ids[0])], context=context)
                    for line_id in line_ids:
                        inventory_line_obj.write(cr, uid, [line_id], {'final_qty': product_line2.get('product_qty')}, context= context)
                else:
                    if product_line2.get('product_qty'):
                        inventory_line_obj.create(cr, uid,{
                                                    'product_id': product_line2.get('product_id'),
                                                    'final_qty': product_line2.get('product_qty'),
                                                    'product_uom': product_line2.get('product_uom'),
                                                    'parent_id': ids[0],
                                                    }, context=context)

    def get_move_inventory_temp(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        inventory_line_obj = self.pool.get('stock.inventory.location.lines.temp')
        if ids and len(ids):
            current_inv= self.browse(cr, uid, ids[0], context=context)
            location= current_inv.emplacement_id.id

            basic_from_date= datetime.datetime.strptime(current_inv.from_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
            from_date= datetime.datetime.strftime(basic_from_date, DEFAULT_SERVER_DATETIME_FORMAT)
            basic_to_date= datetime.datetime.strptime(current_inv.to_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
            obj_dt1= datetime.datetime.combine(basic_to_date, datetime.datetime.min.time()) + datetime.timedelta(days=1) - datetime.timedelta(minutes = 1)
            dt1= datetime.datetime.strftime(obj_dt1, DEFAULT_SERVER_DATETIME_FORMAT)
            move_ids = move_obj.search(cr, uid, [('state','=','done'),
                                                 ('date','>=' , from_date),
                                                 ('date','<=',dt1),
                                                 '|',('location_dest_id','=',location),('location_id','=',location)], context=context)

            list_prod=[]
            prods=[]
            if move_ids:
                for move_id in move_ids:
                    move= move_obj.browse(cr, uid, move_id, context=context)

                    if move.product_id not in prods:
                        if move.location_dest_id.id != move.location_id.id:
                            total_input=0.0
                            total_output= 0.0
                            if move.location_dest_id.id == location:
                                total_input= move.product_uom_qty
                            else:
                                total_output= move.product_uom_qty
                            list_prod.append({'product': move.product_id,
                                              'total_input': total_input,
                                              'total_output': total_output})
                            prods.append(move.product_id)
                    else:
                        list_temp= list(list_prod)
                        for ls in list_temp:
                            if move.product_id==ls.get('product'):
                                if move.location_dest_id.id == location:
                                    total_input= move.product_uom_qty + ls.get('total_input')
                                    total_output= ls.get('total_output')
                                    list_prod.remove(ls)
                                    list_temp.remove(ls)
                                    list_prod.append({'product': move.product_id,
                                                      'total_input': total_input,
                                                      'total_output': total_output})
                                else:
                                    total_input=  ls.get('total_input')
                                    total_output= move.product_uom_qty + ls.get('total_output')
                                    list_prod.remove(ls)
                                    list_temp.remove(ls)
                                    list_prod.append({'product': move.product_id,
                                                      'total_input': total_input,
                                                      'total_output': total_output})

            if list_prod and len(list_prod):
                if current_inv.child_ids:
                    lines=[]
                    for line in current_inv.child_ids:
                        lines.append(line.product_id)
                    for inventory in list_prod:
                        if inventory.get('product') not in lines:
                            inventory_line_obj.create(cr, uid,{
                                                    'product_id': inventory.get('product').id,
                                                    'total_input': inventory.get('total_input'),
                                                    'total_output': inventory.get('total_output'),
                                                    'product_uom': inventory.get('product').uom_id.id,
                                                    'parent_id': ids[0],
                                                    }, context=context)
                        else:
                            for inv in current_inv.child_ids:
                                if inv.product_id == inventory.get('product'):
                                    inventory_line_obj.write(cr, uid, inv.id, {'parent_id': ids[0],
                                                                               'total_input': inventory.get('total_input'),
                                                                               'total_output': inventory.get('total_output')}, context=context)
                else:
                    for inventory in list_prod:
                        inventory_line_obj.create(cr, uid,{
                                                    'product_id': inventory.get('product').id,
                                                    'product_uom': inventory.get('product').uom_id.id,
                                                    'parent_id': ids[0],
                                                    'total_input': inventory.get('total_input'),
                                                    'total_output': inventory.get('total_output')}, context=context)





    def make_inventory_temp2(self, cr, uid, ids, context):
        if ids and len(ids):
            self.fill_init_inventory_product2(cr, uid, ids, context=context)
            self.get_move_inventory_temp(cr, uid, ids, context=context)
            self.fill_final_inventory_product2(cr, uid, ids, context=context)

        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
             }



class stock_inventory_per_location_lines_temp(osv.osv_memory):
    _name = "stock.inventory.location.lines.temp"
    _description = "Product line by Location"
    _rec_name= "product_id"
    _columns = {
        'parent_id': fields.many2one('stock.inventory.location.temp', 'Parent', requires=True, select=True),
        'product_id': fields.many2one('product.product', 'Article', required=True, select=True),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True),

        'beginning_qty': fields.float('Stock Initial',readonly=True),
        'final_qty': fields.float('Stock Final',readonly=True),

        'total_input': fields.float('Total Entree',help="total des articles entr�e dans l'emplacement pendant la periode"),
        'total_output': fields.float('Total Sortie',help="total des articles sortie de l'emplacement pendant la periode"),

    }
