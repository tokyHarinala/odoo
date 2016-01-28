# -*- coding: utf-8 -*-
'''
Created on 26 juil. 2012

@author: Rina
'''

from openerp.osv import osv, fields
from datetime import datetime
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID


#newBaseModel=BaseModel()

class product_template(osv.osv):

    _inherit = "product.template"

    _columns = {
            'purchase_history': fields.one2many('product.purchase.order.history', 'product_tmpl_id', 'purchase history for product'),
            'last_purchase_price': fields.float('Dernier prix achat'),
            'date_last_purchase_price': fields.date('Date dernier achat'),
        }

    def onchange_last_purchase_price(self, cr, uid, last_purchace_price, context):
        write_date= datetime.now().strftime('%Y-%m-%d')
        if last_purchace_price:
            return {'value': {'date_last_purchase_price': write_date}}
        return True



    def action_product_history(self,cr,uid,ids,context):

        current_product= self.pool.get('product.template').browse(cr, uid, ids[0])
        for prod in current_product.product_variant_ids:
            self.pool.get('product.product').action_product_history(cr, uid, [prod.id], context=context)

        return True


product_template()



class product_product(osv.osv):

    _inherit = "product.product"


#####     MISE à JOUR HISTORIQUE DE PRIX   ######
    def create(self, cr, uid, vals, context=None):
        res= super(product_product, self).create(cr, uid, vals, context=context)
        if vals.has_key('last_purchase_price'):
            date_order= datetime.now().strftime('%Y-%m-%d')
            if vals.has_key('date_last_purchase_price'):
                date_order= vals['date_last_purchase_price']
            self.pool.get('product.purchase.order.history').create(cr, uid, {'date_order':date_order,
                                                                             'product_id':res,
                                                                             'product_qty': 1,
                                                                             'price_unit': vals['last_purchase_price'],
                                                                                })
        return res

    def onchange_last_purchase_price(self, cr, uid, last_purchace_price, context):
        write_date= datetime.now().strftime('%Y-%m-%d')
        if last_purchace_price:
            return {'value': {'date_last_purchase_price': write_date}}
        return True



    def check_double_purchase_price(self, cr, uid, date, price, context=None):
        res=False
        if date and price:
            res_ids= self.pool.get('product.purchase.order.history').search(cr,uid,[('date_order','=',date),('price_unit','=',price)])
            if res_ids:
                res=True
        return res



    def write(self, cr, uid, ids, vals, context=None):
        if vals.has_key('last_purchase_price'):

            date_order= datetime.now().strftime('%Y-%m-%d')
            if vals.has_key('date_last_purchase_price'):
                date_order= vals['date_last_purchase_price']
            is_double=self.check_double_purchase_price(cr, uid, date_order, vals['last_purchase_price'], context=context)
            if not is_double:
                if type(ids) in (int, long,):
                    ids= [ids]
                self.pool.get('product.purchase.order.history').create(cr, uid, {'date_order':date_order,
                                                                                 'product_id':ids[0],
                                                                                 'product_qty': 1,
                                                                                 'price_unit': vals['last_purchase_price'],
                                                                                    })
            return super(product_product, self).write(cr, SUPERUSER_ID, ids, vals, context=context)

        return super(product_product, self).write(cr, uid, ids, vals, context=context)

#################


    def action_product_history(self,cr,uid,ids,context):

        obj_purchase_line=self.pool.get('purchase.order.line')

        if type(ids) in (int, long,):
            ids= [ids]

        for current_id in ids:
            list_purchase_history=[]
            current_product= self.pool.get('product.product').browse(cr, uid, current_id)
            current_last_purchase_price= current_product.last_purchase_price or 0.0
            current_date_last_purchase_price= current_product.date_last_purchase_price

            cr.execute('delete from product_purchase_order_history where product_id=%s and name is not null',(current_id,))
            p_line=obj_purchase_line.search(cr,uid,[('product_id','=',current_id),('state','=','confirmed')], order='create_date asc')

            last_price=0
            for line in p_line:

                p_order_line= obj_purchase_line.browse(cr,uid,line)

                if p_order_line.price_unit!= last_price:
                    if p_order_line.order_id:
                        partner_id=p_order_line.order_id.partner_id.id
                        date_order=p_order_line.order_id.date_order
                        order_name=p_order_line.order_id.name
                    else:
                        partner_id=None
                        date_order=None
                        order_name=None

                    purchase_history={
                        'partner_id':partner_id,
                        'date_order':date_order,
                        'product_id':p_order_line.product_id.id,
                        'product_tmpl_id':p_order_line.product_id.product_tmpl_id.id,
                        'product_qty': p_order_line.product_qty,
                        'price_unit': p_order_line.price_unit,
                        'product_uom': p_order_line.product_uom.id,
                        'name':order_name,
                        }

                    list_purchase_history.append(purchase_history)
                last_price= p_order_line.price_unit

            if list_purchase_history:
                if not current_date_last_purchase_price:
                    current_last_purchase_price= list_purchase_history[0].get('price_unit')
                    current_date_last_purchase_price= list_purchase_history[0].get('date_order')

                for p_histo in list_purchase_history:
                    self.pool.get('product.purchase.order.history').create(cr, uid, p_histo)
                    if p_histo.get('date_order') and p_histo.get('date_order') > current_date_last_purchase_price:
                        current_date_last_purchase_price = p_histo.get('date_order')
                        current_last_purchase_price= p_histo.get('price_unit')
                self.pool.get('product.product').write(cr, uid, ids[0], {'last_purchase_price':current_last_purchase_price,
                                                                         'date_last_purchase_price':current_date_last_purchase_price}, context=context)

            else:
                self.pool.get('product.product').write(cr, uid, ids[0], {'last_purchase_price':0.0,
                                                                         'date_last_purchase_price':None}, context=context)

        return True


product_product()


class product_order_history(osv.osv):

    _name = "product.purchase.order.history"
    #_auto = False
    _description = "Historique des commandes produits"

    _columns = {
                'name':fields.char('Ref commande', size=128,readonly=True),
                'date_order':fields.date('Order Date', readonly=True),
                'partner_id':fields.many2one('res.partner', 'Supplier', readonly=True),
                'product_tmpl_id': fields.many2one('product.template', 'Product template',readonly=True),
                'product_id': fields.many2one('product.product', 'Product',readonly=True),
                'product_qty': fields.float('Quantity',digits_compute=dp.get_precision('Product Unit of Measure')),
                'price_unit': fields.float('Unit Price', digits_compute= dp.get_precision('Product Price')),
                'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', readonly=True),

        }


product_order_history()

class purchase_order_line(osv.osv):
    _inherit="purchase.order.line"

    def check_price_history(self, cr, uid, ids, purchase_order_line, context=None ):
        res=False
        if purchase_order_line:
            domain = [('product_id','=',purchase_order_line.product_id.id),
                      ('price_unit','=',purchase_order_line.price_unit)]
            list_ids= self.pool.get('product.purchase.order.history').search(cr, uid, domain, limit=1, order='create_date desc', context=context)
            if list_ids:
                res=True
        return res


    def purchase_order_line_price_history(self, cr, uid, ids, context=None):

        if ids:
            if type(ids) in (int, long,):
                    ids= [ids]
            for p_id in ids:
                current_purchase_order_line= self.pool.get('purchase.order.line').browse(cr, uid, p_id)
                to_create= self.check_price_history(cr, uid, ids, current_purchase_order_line, context)
                date_order= datetime.now()
                if to_create:
                    if current_purchase_order_line.order_id:
                        partner_id=current_purchase_order_line.order_id.partner_id.id
                        date_order=current_purchase_order_line.order_id.date_order
                        order_name=current_purchase_order_line.order_id.name
                    else:
                        partner_id=None
                        order_name=None

                    purchase_history={
                        'partner_id':partner_id,
                        'date_order':date_order,
                        'product_tmpl_id':current_purchase_order_line.product_id.product_tmpl_id.id,
                        'product_id':current_purchase_order_line.product_id.id,
                        'product_qty': current_purchase_order_line.product_qty,
                        'price_unit': current_purchase_order_line.price_unit,
                        'product_uom': current_purchase_order_line.product_uom.id,
                        'name':order_name,
                        }

                    self.pool.get('product.purchase.order.history').create(cr, uid, purchase_history)

                self.pool.get('product.product').write(cr, uid, current_purchase_order_line.product_id.id, {'last_purchase_price':current_purchase_order_line.price_unit,
                                                                             'date_last_purchase_price':date_order}, context=context)

        return True


    def action_confirm(self, cr, uid, ids, context=None):
        self.purchase_order_line_price_history(cr, uid, ids, context=context)
        return super(purchase_order_line, self).action_confirm(cr, uid, ids, context=context)


