# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

class ProductCategory(models.Model):
    _inherit = 'product.category'

    sinc_id = fields.Integer(string='BigCommerce ID', default=0, copy=False, readonly=True)

class Laboratorio(models.Model):
    _inherit = "onlife.laboratorio"

    sinc_id = fields.Integer(string='BigCommerce ID', default=0, copy=False, readonly=True)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    sinc_id = fields.Integer(string='BigCommerce ID', default=0, copy=False, readonly=True)

class ProductCustomFields(models.Model):
    _inherit = "onlife.producto_campo_personalizado"

    sinc_id = fields.Integer(string='BigCommerce ID', default=0, copy=False, readonly=True)
