# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'
    
    sinc_id = fields.Integer(string='BC ID', default=0)
