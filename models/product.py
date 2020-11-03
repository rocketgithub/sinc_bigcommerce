# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

class ProductCategory(models.Model):
    _inherit = 'product.category'

    sinc_id = fields.Integer(string='BigCommerce ID', default=0, copy=False, readonly=True)
    
class Marca(models.Model):
    _name = "sinc_bigcommerce.marca"

    name = fields.Char('Nombre', required=True)
    sinc_id = fields.Integer(string='BigCommerce ID', default=0, copy=False, readonly=True)

    _sql_constraints = [
        ('code_value_uniq', 'unique (name)', 'El nombre de la marca debe ser único !')
    ]

class CampoPersonalizado(models.Model):
    _name = "sinc_bigcommerce.campo_personalizado"
    
    name = fields.Char('Nombre', required=True)

class ProductoCampoPersonalizado(models.Model):
    _name = "sinc_bigcommerce.producto_campo_personalizado"
    _rec_name = 'product_id'

    def _campos_personalizados(self):
        res = []
        fields = self.env['sinc_bigcommerce.campo_personalizado'].search([])
        for field in fields:
            res.append((field.name, field.name))
        return res

    product_id = fields.Many2one('product.template', string='Producto', required=True, ondelete='cascade', index=True, copy=False)
    campo_personalizado_id = fields.Selection(selection=_campos_personalizados, string='Campo personalizado', required=True, store=True)
    value = fields.Char('Valor', required=True)
    sinc_id = fields.Integer(string='BigCommerce ID', default=0, copy=False, readonly=True)

    _sql_constraints = [
        ('code_value_uniq', 'unique (campo_personalizado_id, product_id)', 'El campo personalizado debe ser único por producto !')
    ]

class ProductTemplate(models.Model):
    _inherit = "product.template"

    marca_id = fields.Many2one('sinc_bigcommerce.marca', 'Marca')
    keywords = fields.Char('Search keywords')
    campo_personalizado_ids = fields.One2many('sinc_bigcommerce.producto_campo_personalizado', 'product_id', 'Campo personalizado')
    sinc_id = fields.Integer(string='BigCommerce ID', default=0, copy=False, readonly=True)
