# -*- coding: utf-8 -*-
'''
Created on 23 nov. 2015

@author: Toky
'''


from openerp import models, fields, api
import logging
from openerp.exceptions import Warning

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'


    @api.one
    def is_location_ok(self, location, location_dest):
        is_Ok= True
        if location_dest==location:
            return is_Ok
        if location and location.is_restrict_location and location_dest:
            if location_dest.usage=='internal' and  location_dest not in location.restrict_location_dest_ids:
                is_Ok=False
        return is_Ok



    @api.one
    def is_location_dest_ok(self, location_dest, location):
        is_Ok= True
        if location_dest==location:
            return is_Ok
        if location_dest and location_dest.is_restrict_location and location:
            if location.usage=='internal' and location not in location_dest.restrict_location_ids:
                is_Ok=False
        return is_Ok

    @api.one
    def check_location_retriction(self, location, location_dest):
        location_ok= self.is_location_ok(location, location_dest)
        if not location_ok[0]:
            raise Warning("Vous ne pouvez pas effectuer des transferts de l'emplacement: \n"+self.location_id.name+" vers " +self.location_dest_id.name+" ,\n Veuillez verifier et modifier votre emplacements source et/ou destination")
        location_dest_ok= self.is_location_dest_ok(location_dest, location)
        if not location_dest_ok[0]:
            raise Warning("Vous ne pouvez pas effectuer des transferts de l'emplacement: \n"+self.location_id.name+" vers " +self.location_dest_id.name+" ,\n Veuillez verifier et modifier votre emplacements source et/ou destination")


    @api.onchange('location_id', 'location_dest_id')
    def onchange_location(self):
        if self.location_id and self.location_dest_id:
            self.check_location_retriction(self.location_id, self.location_dest_id)




class StockLocation(models.Model):
    _inherit ='stock.location'

    is_restrict_location = fields.Boolean('Restriction Emplacement')
    restrict_location_ids = fields.Many2many('stock.location', 'stock_location_location_rel','parent_id', 'restrict_location_id', 'Sources autoriser')
    restrict_location_dest_ids = fields.Many2many('stock.location', 'stock_location_location_dest_rel','parent_id', 'restrict_location_dest_id', 'Destinations autoriser')
