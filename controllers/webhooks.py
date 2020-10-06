# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, route
from datetime import datetime
import logging

class Webhooks(http.Controller):
    @route('/clientes', type='http', auth="public")
    def index(self, **kw):
        a = 1
#        logging.warn('HOLA MUNDO...!!!')
        return True

        logging.warn('HOLA MUNDO...')
#        return http.request.render('sinc_bigcommerce.clientes', {})

