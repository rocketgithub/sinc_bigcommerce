# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sinc_id = fields.Integer(string='BigCommerce ID', default=0, copy=False)
