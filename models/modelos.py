# -*- coding: utf-8 -*-

# En este archivo están definidos todos los modelos que relacionan un modelo de Odoo con el respectivo modelo en BigCommerce.
# Todos estos modelos tienen que tener definidos por lo menos los siguientes métodos: 
# model(), campos(), filtro_odoo(), obtener_bc_info()

from odoo import models, fields, api
from odoo.exceptions import UserError
import json
import logging

class SincResPartner(models.AbstractModel):
    _name = 'sinc_bigcommerce.res_partner'
    _inherit = 'sinc_bigcommerce.base'

    # Retorna la version del api de bigcommerce que utiliza el modelo.
    def bc_api_version(self):
        return 'V3'

    # Retorna el modelo de Odoo relacionado.
    def res_model(self):
        return 'res.partner'

    # Retorna un array que relaciona campos de Odoo y BigCommerce. Están permitidas las siguientes estructuras de relación:
    # ['first_name', 'first_name'] => ['campo de Odoo', 'Campo de BigCommerce']
    # ['customer_rank', '=', 1] => ['campo de Odoo', 'constante']
    # ['type', '=', 'other'] => ['campo de Odoo', 'constante']
    # ['name', ' ', 'first_name', 'last_name'] => ['campo de Odoo', 'concatena', 'Campo BigCommerce #1', 'Campo BigCommerce #2']
    def campos(self):
        res = {}
        res['clasicos'] = [
            ['name', ' ', 'first_name', 'last_name'], 
            ['customer_rank', '=', 1], 
            ['email', 'email'], 
            ['sinc_id', 'id']
        ]

        return res

    # Retorna el filtro de Odoo que será utilizado en búsquedas que determinan si un registro de BigCommerce ya existe en Odoo.
    # sinc_id es el campo en Odoo que relaciona al registro de Odoo con el id del registro en BigCommerce.
    def filtro_odoo(self, id):
        return [('sinc_id', '=', id), ('type', '=', 'contact')]

    # En este método se define la llamada al método correspondiente del modelo 'sinc_bigcommerce.api'.
    # En este caso se llama al método get_customers de 'sinc_bigcommerce.api' por ser este modelo el relacionado a los Clientes.
    def obtener_bc_info(self, filtro = None):
        res = self.env['sinc_bigcommerce.api'].get_customers(filtro)
        if res:
            res = json.loads(res)
            return res
        else:
            return False

    # Crea un nuevo registro en Odoo
    def create_odoo(self, dict):
        return self.env[self.res_model()].create(dict)

    # Modifica un registro en Odoo
    def write_odoo(self, dict):
        return self.env[self.res_model()].write(dict)

class SincResPartnerAddress(models.AbstractModel):
    _name = 'sinc_bigcommerce.res_partner_address'
    _inherit = 'sinc_bigcommerce.base'

    def bc_api_version(self):
        return 'V3'

    def res_model(self):
        return 'res.partner'

    def campos(self):
        res = {}
        res['clasicos'] = [
            ['name', ' ', 'first_name', 'last_name'], 
            ['type', '=', 'other'], 
            ['customer_rank', '=', 1], 
            ['street', 'address1'], 
            ['street2', 'address2'], 
            ['city', 'city'], 
            ['zip', 'postal_code'], 
            ['phone', 'phone'], 
            ['sinc_id', 'id'], 
#            ['parent_id', ['customer_id', 'res.partner']]
            ['parent_id', 'customer_id']
        ]

        return res

    def filtro_odoo(self, id):
        return [('sinc_id', '=', id), ('type', '!=', 'contact')]

    def obtener_bc_info(self, filtro = None):
        res = self.env['sinc_bigcommerce.api'].get_customers_addresses(filtro)
        if res:
            res = json.loads(res)
            return res
        else:
            return False

    def _establecer_cliente(self, partner_id):
        cliente = self.env['res.partner'].search([('sinc_id', '=', partner_id), ('type', '=', 'contact')])
        if not cliente:
            filtro = [{'id:in': partner_id}]
            self.env['sinc_bigcommerce.res_partner'].transferir_bc_odoo(filtro)
            cliente = self.env['res.partner'].search([('sinc_id', '=', partner_id)])
        return cliente

    def create_odoo(self, dict):
        cliente = self._establecer_cliente(dict['parent_id'])
        dict['parent_id'] = cliente.id
        return self.env[self.res_model()].create(dict)

    def write_odoo(self, dict):
        cliente = self._establecer_cliente(dict['parent_id'])
        dict['parent_id'] = cliente.id
        return self.env[self.res_model()].write(dict)

class SincProductCategory(models.AbstractModel):
    _name = 'sinc_bigcommerce.product_category'
    _inherit = 'sinc_bigcommerce.base'
    
    def bc_api_version(self):
        return 'V3'

    def res_model(self):
        return 'product.category'

    def campos(self):
        res = {}
        res['clasicos'] = [
            ['name', 'name'], 
            ['sinc_id', 'id'], 
#            ['parent_id', ['parent_id', 'product.category']]
            ['parent_id', 'parent_id']
        ]

        return res

    def filtro_odoo(self, id):
        return [('sinc_id', '=', id)]

    def obtener_bc_info(self, filtro = None):
        res = self.env['sinc_bigcommerce.api'].get_product_categories(filtro)
        if res:
            res = json.loads(res)
            for r in res['data']:
                if r['parent_id'] == 0:
                    r['parent_id'] = False
            return res
        else:
            return False

    def _establecer_categoria(self, categ_id):
        categoria = self.env['product.category'].search([('sinc_id', '=', categ_id)])
        if not categoria:
            filtro = [{'id:in': categ_id}]
            self.env['sinc_bigcommerce.product_category'].transferir_bc_odoo(filtro)
            categoria = self.env['product.category'].search([('sinc_id', '=', categ_id)])
        return categoria

    def create_odoo(self, dict):
        if dict['parent_id']:
            categoria = self._establecer_categoria(dict['parent_id'])
            dict['parent_id'] = categoria.id
        else:
            del dict['parent_id']
        return self.env[self.res_model()].create(dict)

    def write_odoo(self, dict):
        if dict['parent_id']:
            categoria = self._establecer_categoria(dict['parent_id'])
            dict['parent_id'] = categoria.id
        else:
            del dict['parent_id']
        return self.env[self.res_model()].write(dict)

class SincProduct(models.AbstractModel):
    _name = 'sinc_bigcommerce.product'
    _inherit = 'sinc_bigcommerce.base'

    def bc_api_version(self):
        return 'V3'

    def res_model(self):
        return 'product.product'

    def campos(self):
        res = {}
        res['clasicos'] = [
            ['name', 'name'],
            ['categ_id', 'category_id'],
            ['type', 'type'],
            ['weight', 'weight'],
            ['list_price', 'price'],
            ['default_code', 'sku'],
            ['sinc_id', 'id'],
        ]

        return res

    def filtro_odoo(self, id):
        return [('sinc_id', '=', id)]

    def obtener_bc_info(self, filtro = None):
        res = self.env['sinc_bigcommerce.api'].get_products(filtro)
        if res:
            res = json.loads(res)
            for r in res['data']:
                if r['categories'] != []:
                    r['category_id'] = r['categories'][0]
                else:
                    r['category_id'] = False
                    
                r['type'] = 'product'

            return res
        else:
            return False

    def obtener_odoo_info(self, filtro = []):
        return self.env[self.res_model()].search(filtro)

    def _establecer_categoria(self, categ_id):
        categoria = self.env['product.category'].search([('sinc_id', '=', categ_id)])
        if not categoria:
            filtro = [{'id:in': categ_id}]
            self.env['sinc_bigcommerce.product_category'].transferir_bc_odoo(filtro)
            categoria = self.env['product.category'].search([('sinc_id', '=', categ_id)])
        return categoria

    def create_odoo(self, dict):
        categoria = self._establecer_categoria(dict['categ_id'])
        if categoria:
            dict['categ_id'] = categoria.id
            return self.env[self.res_model()].create(dict)
        else:
            return False

    def write_odoo(self, dict):
        categoria = self._establecer_categoria(dict['categ_id'])
        if categoria:
            dict['categ_id'] = categoria.id
            return self.env[self.res_model()].write(dict)
        else:
            return False

    def create_bc(self, dict):
        if dict['category_id']:
            dict['categories'] = [dict['category_id'].sinc_id]
        else:
            dict['categories'] = []
        del dict['category_id']
        dict['type'] = 'physical'

        dict = json.dumps(dict)
        return self.env['sinc_bigcommerce.api'].post_product(dict)

    def write_bc(self, dict, bc_id):        
        if dict['category_id']:
            dict['categories'] = [dict['category_id'].sinc_id]
        else:
            dict['categories'] = []
        del dict['category_id']
        dict['type'] = 'physical'

        dict = json.dumps(dict)
        return self.env['sinc_bigcommerce.api'].put_product(dict, bc_id)

    def delete_bc(self, bc_id):
        return self.env['sinc_bigcommerce.api'].delete_product(bc_id)

class SincOrders(models.AbstractModel):
    _name = 'sinc_bigcommerce.sale'
    _inherit = 'sinc_bigcommerce.base'

    def bc_api_version(self):
        return 'V2'

    def res_model(self):
        return 'sale.order'

    def campos(self):
        res = {}
        res['clasicos'] = [
            ['partner_id', 'customer_id'],
            ['sinc_id', 'id'],
        ]
        res['o2m'] = [
            ['order_line', 
             'order_line', 
             {'clasicos': [['product_id', 'product_id'], ['price_unit', 'base_price'], ['product_uom_qty', 'quantity']]}
            ]
        ]

        return res

    def filtro_odoo(self, id):
        return [('sinc_id', '=', id)]

    def bc_count(self):
        return self.env['sinc_bigcommerce.api'].get_orders_count()

    def obtener_bc_info(self, filtro = None):
        res = self.env['sinc_bigcommerce.api'].get_orders(filtro)
        if res:
            res = json.loads(res)
            for i, r in enumerate(res):
                res[i]['order_line'] = json.loads(self.env['sinc_bigcommerce.api'].get_order_products(r['id']))
            result= {}
            result['data'] = res
            result['meta'] = {}
            result['meta']['pagination'] = {}
            result['meta']['pagination']['total'] = len(res)
            result['meta']['pagination']['current_page'] = 1
            result['meta']['pagination']['total_pages'] = result['meta']['pagination']['current_page'] + 1
            return result
        else:
            return False

    def _establecer_cliente(self, partner_id):
        cliente = self.env['res.partner'].search([('sinc_id', '=', partner_id), ('type', '=', 'contact')])
        if not cliente:
            filtro = [{'id:in': partner_id}]
            self.env['sinc_bigcommerce.res_partner'].transferir_bc_odoo(filtro)
            cliente = self.env['res.partner'].search([('sinc_id', '=', partner_id)])
        return cliente

    def _establecer_producto(self, product_id):
        producto = self.env['product.product'].search([('sinc_id', '=', product_id)])
        if not producto:
            filtro = [{'id:in': product_id}]
            self.env['sinc_bigcommerce.product'].transferir_bc_odoo(filtro)
            producto = self.env['product.product'].search([('sinc_id', '=', product_id)])
        return producto

    def create_odoo(self, dict):
        if dict['partner_id'] == 0:
            dict['partner_id'] = False
        cliente = self._establecer_cliente(dict['partner_id'])
        error = False
        nota = []
        if not cliente:
            error = True
            partner_id = self.env["res.config.settings"].obtener_cliente()
            if partner_id:
                cliente = self.env['res.partner'].search([('id', '=', int(partner_id))])
                if not dict['partner_id']:
                    nota.append('Cliente inexistente ID: 0')
                else:
                    nota.append('Cliente inexistente ID: ' + str(dict['partner_id']))
        
        if cliente:
            dict['partner_id'] = cliente.id
            lineas = []
            for linea in dict['order_line']:
                producto = self._establecer_producto(linea['product_id'])
                if producto:
                    linea['product_id'] = producto.id
                    linea['name'] = producto.display_name
                    lineas.append((0, 0, linea))
                else:
                    error = True
                    nota.append('Producto inexistente ID: ' + str(linea['product_id']))

            dict['order_line'] = lineas
            venta = self.env[self.res_model()].create(dict)

            
            if not error:
                venta.action_confirm()
                venta._create_invoices()
                for factura in venta.invoice_ids:
                    factura.action_post()
            else:
                for n in nota:
                    venta.message_post(body=n)

            return venta
        return False

    def write_odoo(self, dict):
        return False
