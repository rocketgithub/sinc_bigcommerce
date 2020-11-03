# -*- coding: utf-8 -*-

# En este archivo están definidos todos los modelos que relacionan un modelo de Odoo con el respectivo del modelo en BigCommerce.
# Todos estos modelos tienen que tener definidos por lo menos los siguientes métodos: 
# res_model(), campos(), filtro_odoo(), obtener_bc_info()

from odoo import models, fields, api
import json
import requests
import base64
import logging

class SincResPartner(models.AbstractModel):
    _name = 'sinc_bigcommerce.res_partner'
    _inherit = 'sinc_bigcommerce.base'

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
    def obtener_bc_info(self, params):
        res = self.env['sinc_bigcommerce.api'].get_customers(params)
        if res:
            res = json.loads(res)
            return res
        else:
            return False

    # Crea un nuevo registro en Odoo
    def create_odoo(self, dict):
        return self.env[self.res_model()].create(dict)

    # Modifica un registro en Odoo
    def write_odoo(self, obj, dict):
        return obj.write(dict)

    def establecer_cliente(self, partner_id):
        cliente = self.env[self.res_model()].search(self.filtro_odoo(partner_id))
        if not cliente:
            params = [{'id:in': partner_id}]
            self.transferir_bc_odoo(params)
            cliente = self.env[self.res_model()].search(self.filtro_odoo(partner_id))
        return cliente

class SincResPartnerAddress(models.AbstractModel):
    _name = 'sinc_bigcommerce.res_partner_address'
    _inherit = 'sinc_bigcommerce.base'

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
            ['parent_id', 'customer_id']
        ]
        return res

    def filtro_odoo(self, id):
        return [('sinc_id', '=', id), ('type', '!=', 'contact')]

    def obtener_bc_info(self, params):
        res = self.env['sinc_bigcommerce.api'].get_customer_addresses(params)
        if res:
            res = json.loads(res)
            return res
        else:
            return False

    def obtener_odoo_info(self, params):
        return self.env[self.res_model()].search(params)

    def create_odoo(self, dict):
        cliente = self.env['sinc_bigcommerce.res_partner'].establecer_cliente(dict['parent_id'])
        dict['parent_id'] = cliente.id
        return self.env[self.res_model()].create(dict)

    def write_odoo(self, obj, dict):
        cliente = self.env['sinc_bigcommerce.res_partner'].establecer_cliente(dict['parent_id'])
        dict['parent_id'] = cliente.id
        return obj.write(dict)

class SincProductCategory(models.AbstractModel):
    _name = 'sinc_bigcommerce.product_category'
    _inherit = 'sinc_bigcommerce.base'

    def res_model(self):
        return 'product.category'

    def campos(self):
        res = {}
        res['clasicos'] = [
            ['name', 'name'], 
            ['sinc_id', 'id'], 
        ]
        return res

    def filtro_odoo(self, id):
        return [('sinc_id', '=', id)]

    def obtener_bc_info(self, params):
        res = self.env['sinc_bigcommerce.api'].get_product_categories(params)
        if res:
            res = json.loads(res)
            return res
        else:
            return False

    def obtener_odoo_info(self, params):
        return self.env[self.res_model()].search(params)

    def create_odoo(self, dict):
        return self.env[self.res_model()].create(dict)

    def write_odoo(self, obj, dict):
        return obj.write(dict)

    def create_bc(self, dict, registro):
        dict['parent_id'] = 0
        dict = json.dumps(dict)
        return self.env['sinc_bigcommerce.api'].post_product_category(dict)

    def write_bc(self, dict, registro):        
        dict['parent_id'] = 0
        dict = json.dumps(dict)
        return self.env['sinc_bigcommerce.api'].put_product_category(dict, registro.sinc_id)

    def establecer_categoria(self, categ_id):
        if categ_id == 0:
            return False
        categoria = self.env['product.category'].search(self.env['sinc_bigcommerce.product_category'].filtro_odoo(categ_id))
        if not categoria:
            params = [{'id': categ_id}]
            self.env['sinc_bigcommerce.product_category'].transferir_bc_odoo(params)
            categoria = self.env['product.category'].search(self.env['sinc_bigcommerce.product_category'].filtro_odoo(categ_id))
        return categoria

        
class SincMarca(models.AbstractModel):
    _name = 'sinc_bigcommerce.brand'
    _inherit = 'sinc_bigcommerce.base'

    def res_model(self):
        return 'sinc_bigcommerce.marca'

    def campos(self):
        res = {}
        res['clasicos'] = [
            ['name', 'name'], 
            ['sinc_id', 'id'], 
        ]
        return res

    def filtro_odoo(self, id):
        return [('sinc_id', '=', id)]

    def obtener_bc_info(self, params):
        res = self.env['sinc_bigcommerce.api'].get_brands(params)
        if res:
            res = json.loads(res)
            return res
        else:
            return False

    def obtener_odoo_info(self, params):
        return self.env[self.res_model()].search(params)

    def create_odoo(self, dict):
        return self.env[self.res_model()].create(dict)

    def write_odoo(self, obj, dict):
        return obj.write(dict)

    def create_bc(self, dict, registro):
        dict = json.dumps(dict)
        return self.env['sinc_bigcommerce.api'].post_brand(dict)

    def write_bc(self, dict, registro):
#        dict['meta_description'] = ''
        dict = json.dumps(dict)
        return self.env['sinc_bigcommerce.api'].put_brand(dict, registro.sinc_id)

    def establecer_marca(self, brand_id):
        if brand_id == 0:
            return False
        marca = self.env['sinc_bigcommerce.marca'].search(self.env['sinc_bigcommerce.brand'].filtro_odoo(brand_id))
        if not marca:
            params = [{'id': brand_id}]
            self.env['sinc_bigcommerce.brand'].transferir_bc_odoo(params)
            marca = self.env['sinc_bigcommerce.marca'].search(self.env['sinc_bigcommerce.brand'].filtro_odoo(brand_id))
        return marca

class SincProduct(models.AbstractModel):
    _name = 'sinc_bigcommerce.product'
    _inherit = 'sinc_bigcommerce.base'

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
            ['marca_id', 'brand_id'],
            ['description', 'description'],
            ['keywords', 'search_keywords'],
            ['sale_ok', 'availability'],
            ['sale_ok', 'is_visible'],
            ['image_1024', 'url_standard'],            
            ['sinc_id', 'id'],
        ]
        res['o2m'] = [
            ['campo_personalizado_ids', 
             'campo_personalizado_ids', 
             {'clasicos': [['campo_personalizado_id', 'name'], ['value', 'value']]}
            ]
        ]

        return res

    def filtro_odoo(self, id):
        return [('sinc_id', '=', id)]

    def obtener_bc_info(self, params):
        res = self.env['sinc_bigcommerce.api'].get_products(params)
        if res:
            res = json.loads(res)
            for i, r in enumerate(res['data']):
                if res['data'][i]['categories'] != []:
                    res['data'][i]['category_id'] = r['categories'][0]
                else:
                    res['data'][i]['category_id'] = False
                    
                if res['data'][i]['type'] == 'physical':
                    res['data'][i]['type'] = 'product'
                else:
                    res['data'][i]['type'] = 'service'

                if res['data'][i]['images'] != []:
                    res['data'][i]['url_standard'] = r['images'][0]['url_standard']
                else:
                    res['data'][i]['url_standard'] = False

                if res['data'][i]['custom_fields'] != []:
                    res['data'][i]['campo_personalizado_ids'] = r['custom_fields']
                else:
                    res['data'][i]['campo_personalizado_ids'] = []
            return res
        else:
            return False

    def obtener_odoo_info(self, params):
        return self.env[self.res_model()].search(params)

    def create_odoo(self, dict):
        categoria = self.env['sinc_bigcommerce.product_category'].establecer_categoria(dict['categ_id'])
        marca = self.env['sinc_bigcommerce.brand'].establecer_marca(dict['marca_id'])

        if categoria:
            dict['categ_id'] = categoria.id
        else:
            dict['categ_id'] = None

        if marca:
            dict['marca_id'] = marca.id
        else:
            dict['marca_id'] = None
             
        imagen = False
        if dict['image_1024']:
            imagen = base64.b64encode(requests.get(dict['image_1024']).content)
            del dict['image_1024']

        campos = []
        campos_personalizados = self.env['sinc_bigcommerce.campo_personalizado'].search([])
        for campo in campos_personalizados:
            campos.append(campo.name)

        lineas = []
        for linea in dict['campo_personalizado_ids']:
            if linea['campo_personalizado_id'] in campos:
                lineas.append((0, 0, linea))
        dict['campo_personalizado_ids'] = lineas

        producto = self.env[self.res_model()].create(dict)
        if imagen:
            producto.product_tmpl_id.image_1920 = imagen

        return producto

    def write_odoo(self, producto, dict):
        categoria = self.env['sinc_bigcommerce.product_category'].establecer_categoria(dict['categ_id'])
        marca = self.env['sinc_bigcommerce.brand'].establecer_marca(dict['marca_id'])

        if categoria:
            dict['categ_id'] = categoria.id
        else:
            dict['categ_id'] = None

        if marca:
            dict['marca_id'] = marca.id
        else:
            dict['marca_id'] = None

        imagen = False
        if dict['image_1024']:
            imagen = base64.b64encode(requests.get(dict['image_1024']).content)
            del dict['image_1024']

        campos = []
        campos_personalizados = self.env['sinc_bigcommerce.campo_personalizado'].search([])
        for campo in campos_personalizados:
            campos.append(campo.name)

        lineas = []
        for campo_personalizado_id in producto.campo_personalizado_ids:
            lineas.append((2, campo_personalizado_id.id, False))

        for linea in dict['campo_personalizado_ids']:
            if linea['campo_personalizado_id'] in campos:
                lineas.append((0, 0, linea))
        dict['campo_personalizado_ids'] = lineas

        producto.write(dict)
        
        if imagen:
            producto.product_tmpl_id.image_1920 = imagen

        return True

    def create_bc(self, dict, producto):
        if dict['category_id']:
            dict['categories'] = [dict['category_id'].sinc_id]
        else:
            dict['categories'] = []
        del dict['category_id']

        if dict['brand_id']:
            dict['brand_id'] = dict['brand_id'].sinc_id
        else:
            del dict['brand_id']

        if dict['type'] == 'product':
            dict['type'] = 'physical'
        else:
            dict['type'] = 'digital'

        if dict['availability']:
            dict['availability'] = 'available'
        else:
            dict['availability'] = 'disabled'

        if not dict['description']:
            del dict['description']

        if not dict['sku']:
            del dict['sku']

        if not dict['search_keywords']:
            del dict['search_keywords']

        image_url = self.env["ir.config_parameter"].get_param("web.base.url", default=None) + '/web/image/product.product/' + str(producto.id) + '/image_1024'
        dict['images'] = [{"image_url": image_url, "is_thumbnail": True}]

        campos_personalizados = []
        if producto.campo_personalizado_ids:
            for campo_personalizado in producto.campo_personalizado_ids:
                campos_personalizados.append({'name': campo_personalizado.campo_personalizado_id, 'value': campo_personalizado.value})
        dict['custom_fields'] = campos_personalizados

        if 'url_standard' in dict:
            del dict['url_standard']

        dict = json.dumps(dict)
        bc_id = self.env['sinc_bigcommerce.api'].post_product(dict)
        
        return bc_id

    def write_bc(self, dict, producto):        
        if dict['category_id']:
            dict['categories'] = [dict['category_id'].sinc_id]
        else:
            dict['categories'] = []
        del dict['category_id']

        if dict['brand_id']:
            dict['brand_id'] = dict['brand_id'].sinc_id
        else:
            del dict['brand_id']

        if dict['type'] == 'product':
            dict['type'] = 'physical'
        else:
            dict['type'] = 'digital'

        if dict['availability']:
            dict['availability'] = 'available'
        else:
            dict['availability'] = 'disabled'

        if not dict['description']:
            del dict['description']

        if not dict['sku']:
            del dict['sku']

        if not dict['search_keywords']:
            del dict['search_keywords']

        image_url = self.env["ir.config_parameter"].get_param("web.base.url", default=None) + '/web/image/product.product/' + str(producto.id) + '/image_1024'
        dict['images'] = [{"image_url": image_url, "is_thumbnail": True}]

        res = self.env['sinc_bigcommerce.api'].get_custom_fields(producto.sinc_id)
        if res:
            res = json.loads(res)
            for r in res['data']:
                self.env['sinc_bigcommerce.api'].delete_custom_field(producto.sinc_id, r['id'])

        campos_personalizados = []
        if producto.campo_personalizado_ids:
            for campo_personalizado in producto.campo_personalizado_ids:
                campos_personalizados.append({'name': campo_personalizado.campo_personalizado_id, 'value': campo_personalizado.value})
        dict['custom_fields'] = campos_personalizados

        if 'url_standard' in dict:
            del dict['url_standard']

        dict = json.dumps(dict)
        bc_id = self.env['sinc_bigcommerce.api'].put_product(dict, producto.sinc_id) 

        return bc_id

    def transferir_odoo_bc(self, filtros = []):
#        self.env['sinc_bigcommerce.product_category'].transferir_odoo_bc([])
#        self.env['sinc_bigcommerce.brand'].transferir_odoo_bc([])
        super(SincProduct, self).transferir_odoo_bc(filtros)

    def establecer_producto(self, product_id):
        producto = self.env['product.product'].search(self.env['sinc_bigcommerce.product'].filtro_odoo(product_id))
        if not producto:
            params = [{'id': product_id}]
            self.env['sinc_bigcommerce.product'].transferir_bc_odoo(params)
            producto = self.env['product.product'].search(self.env['sinc_bigcommerce.product'].filtro_odoo(product_id))
        return producto

class SincOrders(models.AbstractModel):
    _name = 'sinc_bigcommerce.sale'
    _inherit = 'sinc_bigcommerce.base'

    def res_model(self):
        return 'sale.order'

    def campos(self):
        res = {}
        res['clasicos'] = [
            ['partner_id', 'customer_id'],
            ['street', 'street_1'],
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

    def obtener_bc_info(self, params):
        if len(params) == 3 and 'order_id' in params[2]:
            res = self.env['sinc_bigcommerce.api'].get_order(params[2]['order_id'])
        else:
            res = self.env['sinc_bigcommerce.api'].get_orders(params)

        if res:
            res = json.loads(res)
            for i, r in enumerate(res):
                res[i]['street_1'] = r['billing_address']['street_1']
                lines = json.loads(self.env['sinc_bigcommerce.api'].get_order_products(r['id']))
                res[i]['order_line'] = lines
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

    def create_odoo(self, dict):
        if dict['partner_id'] == 0:
            dict['partner_id'] = False
        cliente = self.env['sinc_bigcommerce.res_partner'].establecer_cliente(dict['partner_id'])
        error = False
        nota = []
        if not cliente:
            error = True
            partner_id = self.env["res.config.settings"].obtener_cliente()
            if partner_id:
                cliente = self.env['res.partner'].search(self.env['sinc_bigcommerce.res_partner'].filtro_odoo(int(partner_id)))
                if not dict['partner_id']:
                    nota.append('Cliente inexistente ID: 0')
                else:
                    nota.append('Cliente inexistente ID: ' + str(dict['partner_id']))

        if cliente:
            self.env['sinc_bigcommerce.res_partner_address'].transferir_bc_odoo([{'customer_id:in': cliente.sinc_id}])
            contacto = self.env['sinc_bigcommerce.res_partner_address'].obtener_odoo_info([('parent_id', '=', cliente.id), ('street', '=', dict['street'])])
            del dict['street']
            if contacto:
                dict['partner_id'] = contacto.id
                dict['partner_shipping_id'] = contacto.id
            else:
                dict['partner_id'] = cliente.id
                dict['partner_shipping_id'] = cliente.id

            lineas = []
            for linea in dict['order_line']:
                producto = self.env['sinc_bigcommerce.product'].establecer_producto(linea['product_id'])

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

    def write_odoo(self, obj, dict):
        return False

