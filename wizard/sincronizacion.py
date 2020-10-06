# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import xlsxwriter
import base64
import io
from datetime import datetime, timedelta
import logging

        
class ClientePorIDWizard(models.TransientModel):
    _name = "sinc_bigcommerce.cliente_por_id.wizard"

    cliente_id = fields.Char('ID del cliente')

    #Sincroniza cliente por id
    def sincronizar(self):
        filtro = [{'id:in': self.cliente_id}]
        self.env['sinc_bigcommerce.res_partner'].transferir_bc_odoo(filtro)
        return {'type': 'ir.actions.act_window_close'}

class DireccionesPorClienteIDWizard(models.TransientModel):
    _name = "sinc_bigcommerce.direcciones_por_cliente_id.wizard"

    cliente_id = fields.Char('ID del cliente')

    #Sincroniza direcciones por cliente
    def sincronizar(self):
        filtro = [{'customer_id:in': self.cliente_id}]
        self.env['sinc_bigcommerce.res_partner_address'].transferir_bc_odoo(filtro)
        return {'type': 'ir.actions.act_window_close'}
