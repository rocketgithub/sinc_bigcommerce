# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

# El modelo 'sinc_bigcommerce.base' define varios métodos que son utilizados por varios modelos del módulo de sincronización.
# Esta clase está diseñada para ser heredada por otros modelos, y no para crear instancias de la misma.
class SincBase(models.AbstractModel):
    _name = 'sinc_bigcommerce.base'

    #El primer bloque de métodos de este modelo corresponden a la sincronización BC --> Odoo
    
    # Convierte el diccionario proveniente de BigCommerce en un diccionario para agregar o modificar en Odoo.
    # registro: diccionario de un registro obtenido de BigCommerce.
    # return: diccionario para agregar o modificar en formato Odoo.
    def _preparar_diccionario_odoo(self, registro):
        # Cada modelo de este módulo de sincronización que llama a este método (transferir_bc_odoo), 
        # debe tener definido un método llamado campos().
        campos = self.campos()
        dict = {}
        if 'clasicos' in campos:
            dict = self._preparar_campos_clasicos(registro, campos['clasicos'])

        if 'o2m' in campos:
            o2m_dict = self._preparar_campos_o2m(registro, campos['o2m'])
            for campo in o2m_dict:
                dict[campo] = o2m_dict[campo]

        return dict

    # Crea el diccionario de todos los campos que no son One2many.
    def _preparar_campos_clasicos(self, registro, campos):
        dict = {}
        for campo in campos:
            if len(campo) > 2:
                if campo[1] == ' ':
                    cadena = registro[campo[2]]
                    for x in xrange(3, len(campo)):
                        cadena += campo[1] + registro[campo[x]]
                    dict[campo[0]] = cadena
                elif campo[1] == '=':
                    dict[campo[0]] = campo[2]
            else:
                dict[campo[0]] = registro[campo[1]]
        return dict

    # Crea el diccionario de los campos que son One2many.
    def _preparar_campos_o2m(self, registro, campos):
        dict = {}
        for campo in campos:
            lineas = []
            for linea in registro[campo[1]]:
                lineas.append(self._preparar_campos_clasicos(linea, campo[2]['clasicos']))
            dict[campo[0]] = lineas

        return dict

    def establecer_registro_odoo(self, params):
        if 'id' in params[0]:
            id = params[0]['id']
        else:
            id = params[0]['id:in']

        if id == 0:
            return False
        res = self.env[self.res_model()].search(self.filtro_odoo(id))
        if not res:
            self.transferir_bc_odoo(params)
            res = self.env[self.res_model()].search(self.filtro_odoo(id))
        return res

    # Transfiere información desde BigCommerce hacia Odoo. 
    # params: array de diccionarios para filtrar la búsqueda. Ejemplo: transferir_bc_odoo([{'status_id': 9}])
    def transferir_bc_odoo(self, params = []):
        # El API de BigCommerce V3 hace paginación. El ciclo while se ejecutará hasta que se hayan recorrido el 
        # total de páginas de la consulta.
        params.insert(0, {'limit': self.env['sinc_bigcommerce.api'].get_limit()})
        params.insert(0, {'page': None})
        pagina = 1 #Variable que lleva el control de las páginas.
        contador = 0 #Variable utilizada para desplegar información en el log.
        seguir = True
        while seguir:
            params[0]['page'] = pagina
            # Cada modelo de este módulo de sincronización que llama a este método (transferir_bc_odoo), 
            # debe tener definido un método llamado obtener_bc_info().            
            registros_bc = self.obtener_bc_info(params)
            if registros_bc:
                for registro in registros_bc['data']:
                    dict = self._preparar_diccionario_odoo(registro)
                    # Cada modelo de este módulo de sincronización que llama a este método (transferir_bc_odoo), 
                    # debe tener definido un método llamado res_model() y otro llamado filtro_odoo().
                    obj = self.env[self.res_model()].search(self.filtro_odoo(registro['id']))
                    contador += 1
                    if not obj:
                        logging.warn(str(contador) + ' -- ' + self.res_model() + ' (Crear) BC ID: ' + str(dict['sinc_id']) + ' --> Odoo')
                        obj = self.env[self._name].create_odoo(dict)
                    else:
                        logging.warn(str(contador) + ' -- ' + self.res_model() + ' (Modificar) BC ID: ' + str(dict['sinc_id']) + ' --> Odoo ID: ' + str(obj.id))
                        self.env[self._name].write_odoo(obj, dict)

                # Condición que revisa si termina el ciclo o si se hace una nueva llamada al api de bigcommerce para accesar 
                # la siguiente página de información.
                if registros_bc['meta']['pagination']['current_page'] >= registros_bc['meta']['pagination']['total_pages']:
                    seguir = False
                else:
                    pagina += 1
            else:
                seguir = False

#            if contador > 50:
#                seguir = False

    #El segundo bloque de métodos de este modelo corresponden a la sincronización Odoo --> BC

    # Obtiene un objeto de Odoo y devuelve el diccionario para crear o modificar registros en BigCommerce.
    def _preparar_diccionario_bc(self, registro):
        dict = {}
        campos = self.campos()
        for campo in campos['clasicos']:
            if len(campo) == 2:
                if not isinstance(campo[1], list) and campo[0] != 'sinc_id':
                    dict[campo[1]] = registro[campo[0]]
        return dict

    # Crea o modifica registros en BigCommerce.
    def transferir_odoo_bc(self, params = []):
        registros = self.obtener_odoo_info(params)
        if registros:
            total = len(registros)
            contador = 0
            for registro in registros:
                contador += 1
                dict = self._preparar_diccionario_bc(registro)
                if registro.sinc_id == 0:
                    logging.warn(str(contador) + '/' + str(total) + ' ' + self.res_model() + ' (Crear) Odoo ID: ' + str(registro.id) + ' --> BC')
                    bc_id = self.create_bc(dict, registro)
                    if bc_id:
                        registro.sinc_id = bc_id
                else:
                    logging.warn(str(contador) + '/' + str(total) + ' ' + self.res_model() + ' (Modificar) Odoo ID: ' + str(registro.id) + ' --> BC ID: ' + str(registro.sinc_id))
                    self.write_bc(dict, registro)
