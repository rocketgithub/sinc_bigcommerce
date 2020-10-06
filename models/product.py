# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = 'product.category'

    sinc_id = fields.Integer(string='BC ID', default=0)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    sinc_id = fields.Integer(string='BC ID', default=0)
