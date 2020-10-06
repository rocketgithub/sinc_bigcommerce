# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging

class SincBigCommerceApi(models.AbstractModel):
    _name = 'sinc_bigcommerce.api'

    # Retorna el url base que utiliza BigCommerce en su API V2.
    def _url_base_v2(self):
        return 'https://api.bigcommerce.com/stores/' + self.env["res.config.settings"].obtener_store_hash() + '/v2'

    # Retorna el url base que utiliza BigCommerce en su API V3.
    def _url_base_v3(self):
        return 'https://api.bigcommerce.com/stores/' + self.env["res.config.settings"].obtener_store_hash() + '/v3'

    # Retorna el numero de registros que el api de bigcommerce retornara en las busquedas.
    def get_limit(self):
        return 100

    # Obtiene los customers de BigCommerce. 
    def get_customers(self, filtro=None):
        url = self._url_base_v3() + '/customers?' + str(filtro)
        return self.env['sinc_bigcommerce.requests'].get(url)

    # Obtiene las direcciones de BigCommerce. 
    def get_customers_addresses(self, filtro=None):
        url = self._url_base_v3() + '/customers/addresses?' + str(filtro)
        return self.env['sinc_bigcommerce.requests'].get(url)

    # Obtiene las categorias de productos de BigCommerce. 
    def get_product_categories(self, filtro=None):
        url = self._url_base_v3() + '/catalog/categories?' + str(filtro)
        return self.env['sinc_bigcommerce.requests'].get(url)

    # Obtiene los productos de BigCommerce. 
    def get_products(self, filtro=None):
        url = self._url_base_v3() + '/catalog/products?' + str(filtro)
        return self.env['sinc_bigcommerce.requests'].get(url)

    # Crea un producto en BigCommerce. 
    def post_product(self, dict):
        url = self._url_base_v3() + '/catalog/products'
        return self.env['sinc_bigcommerce.requests'].post(url, dict)

    # Modifica un producto en BigCommerce. 
    def put_product(self, dict, id):
        url = self._url_base_v3() + '/catalog/products/' + str(id)
        return self.env['sinc_bigcommerce.requests'].put(url, dict)

    # Borra un producto en BigCommerce. 
    def delete_product(self, id):
        url = self._url_base_v3() + '/catalog/products/?id:in=' + str(id)
        return self.env['sinc_bigcommerce.requests'].delete(url)

    # Obtiene las ordenes de BigCommerce. 
    def get_orders(self, filtro=None):
        url = self._url_base_v2() + '/orders?' + str(filtro)
        return self.env['sinc_bigcommerce.requests'].get(url)        

    # Obtiene las lineas de una orden de BigCommerce. 
    def get_order_products(self, filtro):
        url = self._url_base_v2() + '/orders/' + str(filtro) + '/products'
        return self.env['sinc_bigcommerce.requests'].get(url)
