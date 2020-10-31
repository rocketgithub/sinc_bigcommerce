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
        return 250

    def _get_params(self, params):
        res = ''
        x = 0
        for p in params:
            for key in p.keys():
                if x == 0:
                    res += key + '=' + str(p[key])
                    x += 1
                else:
                    res += '&' + key + '=' + str(p[key])

        return res

    #CUSTOMERS ----------------------------------------------------------------

    # Obtiene los clientes de BigCommerce.
    def get_customers(self, params):
        url = self._url_base_v3() + '/customers?' + self._get_params(params)
        return self.env['sinc_bigcommerce.requests'].get(url)

    #ADDRESSES ----------------------------------------------------------------

    # Obtiene las direcciones de cliente de BigCommerce. 
    def get_customer_addresses(self, params):
        url = self._url_base_v3() + '/customers/addresses?' + self._get_params(params)
        return self.env['sinc_bigcommerce.requests'].get(url)

    #PRODUCT CATEGORIES -------------------------------------------------------

    # Obtiene las categorias de productos de BigCommerce. 
    def get_product_categories(self, params):
        if len(params) < 3:
            url = self._url_base_v3() + '/catalog/categories?' + self._get_params(params)
        elif len(params) == 3 and params[2]['category_id']:
            url = self._url_base_v3() + '/catalog/categories/' + str(params[2]['category_id'])
        return self.env['sinc_bigcommerce.requests'].get(url)

    # Crea una categoria de producto en BigCommerce. 
    def post_product_category(self, dict):
        url = self._url_base_v3() + '/catalog/categories'
        return self.env['sinc_bigcommerce.requests'].post(url, dict)

    # Modifica una categoria de producto en BigCommerce. 
    def put_product_category(self, dict, category_id):
        url = self._url_base_v3() + '/catalog/categories/' + str(category_id)
        return self.env['sinc_bigcommerce.requests'].put(url, dict)

    #PRODUCTS -----------------------------------------------------------------

    # Obtiene los productos de BigCommerce. 
    def get_products(self, params):
        url = self._url_base_v3() + '/catalog/products?include=images,custom_fields&' + self._get_params(params)
        return self.env['sinc_bigcommerce.requests'].get(url)

    # Crea un producto en BigCommerce. 
    def post_product(self, dict):
        url = self._url_base_v3() + '/catalog/products?include=custom_fields'
        return self.env['sinc_bigcommerce.requests'].post(url, dict)

    # Modifica un producto en BigCommerce. 
    def put_product(self, dict, product_id):
        url = self._url_base_v3() + '/catalog/products/' + str(product_id) + '?include=custom_fields'
        return self.env['sinc_bigcommerce.requests'].put(url, dict)

    # Borra un producto en BigCommerce. 
    def delete_product(self, product_id):
        url = self._url_base_v3() + '/catalog/products/?id:in=' + str(product_id)
        return self.env['sinc_bigcommerce.requests'].delete(url)
        
    #PRODUCT IMAGES -----------------------------------------------------------

    # Obtiene los productos de BigCommerce. 
    def get_product_images(self, product_id):
        url = self._url_base_v3() + '/catalog/products/' + str(product_id) + '/images'
        return self.env['sinc_bigcommerce.requests'].get(url)

    # Crea una imagen en el producto de BigCommerce. 
    def post_product_image(self, product_id, dict):
        url = self._url_base_v3() + '/catalog/products/' + str(product_id) + '/images'
        return self.env['sinc_bigcommerce.requests'].post(url, dict)    

    # Borra una imagen del producto en BigCommerce. 
    def delete_product_image(self, product_id, image_id):
        url = self._url_base_v3() + '/catalog/products/' + str(product_id) + '/images/' + str(image_id)
        return self.env['sinc_bigcommerce.requests'].delete(url)

    #PRODUCT CUSTOM FIELDS ----------------------------------------------------

    # Obtiene los productos de BigCommerce. 
    def get_custom_fields(self, product_id):
        url = self._url_base_v3() + '/catalog/products/' + str(product_id) + '/custom-fields'
        return self.env['sinc_bigcommerce.requests'].get(url)

    # Crea un campo personalizado en BigCommerce. 
    def post_custom_field(self, product_id, dict):
        url = self._url_base_v3() + '/catalog/products/' + str(product_id) + '/custom-fields'
        return self.env['sinc_bigcommerce.requests'].post(url, dict)

    # Modifica un campo personalizado en BigCommerce. 
    def put_custom_field(self, product_id, campo_personalizado_id, dict):
        url = self._url_base_v3() + '/catalog/products/' + str(product_id) + '/custom-fields/' + str(campo_personalizado_id)
        return self.env['sinc_bigcommerce.requests'].put(url, dict)

    # Borra un campo personalizado en BigCommerce. 
    def delete_custom_field(self, product_id, campo_personalizado_id):
        url = self._url_base_v3() + '/catalog/products/' + str(product_id) + '/custom-fields/' + str(campo_personalizado_id)
        return self.env['sinc_bigcommerce.requests'].delete(url)

    #BRANDS -------------------------------------------------------------------

    # Obtiene las marcas de BigCommerce. 
    def get_brands(self, params):
        if len(params) < 3:
            url = self._url_base_v3() + '/catalog/brands?' + self._get_params(params)
        elif len(params) == 3 and params[2]['brand_id']:
            url = self._url_base_v3() + '/catalog/brands/' + str(params[2]['brand_id'])
        return self.env['sinc_bigcommerce.requests'].get(url)

    # Crea una marca en BigCommerce. 
    def post_brand(self, dict):
        url = self._url_base_v3() + '/catalog/brands'
        return self.env['sinc_bigcommerce.requests'].post(url, dict)

    # Modifica una marca en BigCommerce. 
    def put_brand(self, dict, brand_id):
        url = self._url_base_v3() + '/catalog/brands/' + str(brand_id)
        return self.env['sinc_bigcommerce.requests'].put(url, dict)

    #ORDERS -------------------------------------------------------------------

    def get_order(self, order_id):
        url = self._url_base_v2() + '/orders/' + str(order_id)        
        return self.env['sinc_bigcommerce.requests'].get(url)        

    # Obtiene las ordenes de BigCommerce. 
    def get_orders(self, params):
        url = self._url_base_v2() + '/orders?' + self._get_params(params)
        return self.env['sinc_bigcommerce.requests'].get(url)        

    # Obtiene las lineas de una orden de BigCommerce. 
    def get_order_products(self, order_id):
        url = self._url_base_v2() + '/orders/' + str(order_id) + '/products'
        return self.env['sinc_bigcommerce.requests'].get(url)
