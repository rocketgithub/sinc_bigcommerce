# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
        
class ClientePorIDWizard(models.TransientModel):
    _name = "sinc_bigcommerce.cliente_por_id.wizard"

    cliente_id = fields.Char('ID del cliente', required=True)

    #Sincroniza cliente por id
    def sincronizar(self):
        params = [{'id:in': self.cliente_id}]
        self.env['sinc_bigcommerce.res_partner'].transferir_bc_odoo(params)
        return {'type': 'ir.actions.act_window_close'}

class DireccionesPorClienteIDWizard(models.TransientModel):
    _name = "sinc_bigcommerce.direcciones_por_cliente_id.wizard"

    cliente_id = fields.Char('ID del cliente', required=True)

    #Sincroniza direcciones por cliente
    def sincronizar(self):
        params = [{'customer_id:in': self.cliente_id}]
        self.env['sinc_bigcommerce.res_partner_address'].transferir_bc_odoo(params)
        return {'type': 'ir.actions.act_window_close'}
