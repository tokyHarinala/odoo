# -*- coding: utf-8 -*-
'''
Created on 25 nov. 2015

@author: Toky
'''



from openerp import models, fields, api
import datetime
import logging
from openerp.exceptions import Warning

_logger = logging.getLogger(__name__)


class SuiviDifferenceEmplacement(models.TransientModel):
    _name='wso.stock.inventory.track.difference'

    @api.model
    def _get_selection_year(self):
        now= datetime.datetime.now()
        year_now= now.year
        last_year=year_now - 1
        return [(str(last_year), str(last_year)),(str(year_now),str(year_now))]

    name = fields.Char(default='SUIVI DES ECARTS', readonly=True)
    year = fields.Selection('_get_selection_year', string='Annee', default=str(datetime.datetime.now().year))
    month = fields.Selection([('01','January'),('02','February'), ('03','March'), ('04','April'),
            ('05','May'),('06','June'),('07','July'),('08','August'), ('09','September'),
            ('10','October'), ('11','November'), ('12','December')], 'Mois', default=str(datetime.datetime.now().month))
    location_id = fields.Many2one('stock.location', string="Emplacement", required=True)
    line_ids = fields.One2many('wso.stock.inventory.track.difference.lines', 'parent_id', string='Lignes des Ecarts')



    @api.one
    def compute_difference(self):
        if self.location_id and self.year and self.month:
            if type(self.id) in (int,long):
                self._cr.execute('delete from wso_stock_inventory_track_difference_lines where parent_id=%s', (self.id,))
                my_date= self.year+'-'+self.month+'-'
                inventory_list= self.env['stock.inventory'].search([('date','like',my_date),('state','=','done'),('location_id','=',self.location_id.id)])
                list_move={}
                for inventory in inventory_list:
                    for move in inventory.move_ids:
                        if move.product_id.id not in list_move.keys():
                            qty=0
                            if move.location_id.id== self.location_id.id:
                                qty= move.product_uom_qty
                            else:
                                qty= -move.product_uom_qty
                            list_move[move.product_id.id]={'product_id':move.product_id.id, 'qty': qty}
                        else:
                            qty2=0
                            if move.location_id.id== self.location_id.id:
                                qty2= move.product_uom_qty
                            else:
                                qty2= -move.product_uom_qty
                            list_move[move.product_id.id][qty]+=qty2

                for line_key in list_move.keys():
                    if list_move[line_key].get('qty')>0:
                        self.env['wso.stock.inventory.track.difference.lines'].create({'product_id':list_move[line_key].get('product_id'),
                                                                                       'extra_product_qty':list_move[line_key].get('qty'),
                                                                                       'parent_id': self.id})
                    else:
                        self.env['wso.stock.inventory.track.difference.lines'].create({'product_id':list_move[line_key].get('product_id'),
                                                                                       'miss_product_qty': -list_move[line_key].get('qty'),
                                                                                       'parent_id': self.id})






class SuiviDifferenceEmplacementLines(models.TransientModel):
    _name='wso.stock.inventory.track.difference.lines'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Article", required=True, ondelete='cascade')
    product_uom_id= fields.Many2one('product.uom', string="Unite", related='product_id.uom_id',)
    extra_product_qty = fields.Float(string='Ecart:surplus')
    miss_product_qty = fields.Float(string='Ecart:manque')
    parent_id = fields.Many2one('wso.stock.inventory.track.difference', string="Parent", ondelete='cascade')
