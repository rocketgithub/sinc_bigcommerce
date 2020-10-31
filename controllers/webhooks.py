# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, route
import json
import logging

class Webhooks(http.Controller):
    @route('/webhooks', type='json', auth="public")
    def index(self, **kw):

        args = json.loads(request.httprequest.data)
        producer = 'stores/' + request.env["res.config.settings"].sudo().obtener_store_hash()
        if args and args['producer'] and args['producer'] == producer and args['scope'] and args['data'] and args['data']['id']:
            #Customers
            if args['scope'] == 'store/customer/created' or args['scope'] == 'store/customer/updated':
                logging.warn('Webhook - Customers')
                params = [{'id:in': args['data']['id']}]
                request.env['sinc_bigcommerce.res_partner'].sudo().transferir_bc_odoo(params)
            #Address
            elif args['scope'] == 'store/customer/address/created' or args['scope'] == 'store/customer/address/updated':
                logging.warn('Webhook - Address')
                params = [{'customer_id:in': args['data']['address']['customer_id']}, {'id:in': args['data']['id']}]
                request.env['sinc_bigcommerce.res_partner_address'].sudo().transferir_bc_odoo(params)
            #Orders
            elif args['scope'] == 'store/order/statusUpdated' and args['data']['status'] and args['data']['status']['previous_status_id'] == 11 and args['data']['status']['new_status_id'] == 9:
                logging.warn('Webhook - Orders')
                params = [{'order_id': args['data']['id']}]
                request.env['sinc_bigcommerce.sale'].sudo().transferir_bc_odoo(params)
