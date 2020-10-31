# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    client_id = fields.Char('client_id', default='7xgu6qz4km0vz35u7u4exbdjvc10ao7', config_parameter='sinc.client_id')
    store_hash = fields.Char('store_hash', default='l5lq9lg0om', config_parameter='sinc.store_hash')
    access_token = fields.Char('access_token', default='2y587aim2w6yo833f8j5azlqmxpv0nq', config_parameter='sinc.access_token')
    partner_id = fields.Many2one('res.partner', string='Cliente', config_parameter='sinc.partner_id')

    def get_default_client_id(self, fields):
        client_id = self.env["ir.config_parameter"].get_param("sinc.client_id", default=None)
        return {'client_id': client_id or False}

    def set_client_id(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("sinc.client_id", record.client_id or '')

    def get_default_store_hash(self, fields):
        store_hash = self.env["ir.config_parameter"].get_param("sinc.store_hash", default=None)
        return {'store_hash': store_hash or False}

    def set_store_hash(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("sinc.store_hash", record.store_hash or '')

    def get_default_access_token(self, fields):
        access_token = self.env["ir.config_parameter"].get_param("sinc.access_token", default=None)
        return {'access_token': access_token or False}

    def set_access_token(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("sinc.access_token", record.access_token or '')

    def obtener_client_id(self):
        return self.env["ir.config_parameter"].get_param("sinc.client_id")

    def obtener_store_hash(self):
        return self.env["ir.config_parameter"].get_param("sinc.store_hash")

    def obtener_access_token(self):
        return self.env["ir.config_parameter"].get_param("sinc.access_token")

    def obtener_cliente(self):
        return self.env["ir.config_parameter"].get_param("sinc.partner_id")
