# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

# El modelo 'sinc_bigcommerce.base' define varios métodos que son utilizados por varios modelos del módulo de sincronización.
# Esta clase está diseñada para ser heredada por otros modelos, y no para crear instancias de la misma.
class SincBase(models.AbstractModel):
    _name = 'sinc_bigcommerce.base'

    # Convierte el diccionario proveniente de BigCommerce en un diccionario para agregar o modificar en Odoo.
    # Puede ser utilizado por cualquier modelo que herede de la clase sinc_bigcommerce.base.
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
#            elif isinstance(campo[1], list):
#                obj = self.env[campo[1][1]].search([('sinc_id', '=', registro[campo[1][0]])])
#                dict[campo[0]] = obj.id
            else:
                dict[campo[0]] = registro[campo[1]]
        return dict

    def _preparar_campos_o2m(self, registro, campos):
        dict = {}
        for campo in campos:
            lineas = []
            for linea in registro[campo[1]]:
                lineas.append(self._preparar_campos_clasicos(linea, campo[2]['clasicos']))
            dict[campo[0]] = lineas

        return dict

        
    def _get_params(self, filtros):
        if filtros == None or filtros == []:
            return False

        params = ''
        for filtro in filtros:
            for key in filtro.keys():
                params += '&' + key + '=' + str(filtro[key])
        return params

    # Transfiere información desde BigCommerce hacia Odoo. 
    # Si el método es llamado sin el parámetro 'filtros', se obtienen todos los registros del modelo de BigCommerce.
    # Si el método es llamado con el parámetro 'filtros', se asume que es un id de un modelo de BigCommerce, y se
    # obtiene el registro específico para ese id.
    # Puede ser utilizado por cualquier modelo que herede de la clase sinc_bigcommerce.base.
    # filtros: id del registro en BigCommerce
    def transferir_bc_odoo(self, filtros = None):

        # El API de BigCommerce V3 hace paginación, en bloques de 50 registros. 
        # El ciclo while se ejecutará hasta que se hayan recorrido el total de páginas de la consulta.
        seguir = True
        pagina = 1
        p = self._get_params(filtros)
        while seguir:
            # Cada modelo de este módulo de sincronización que llama a este método (transferir_bc_odoo), 
            # debe tener definido un método llamado obtener_bc_info().
            params = 'page=' + str(pagina) + '&limit=' + str(self.env['sinc_bigcommerce.api'].get_limit())
            if p:
                params += p
            registros_bc = self.obtener_bc_info(params)
            if registros_bc:
                for registro in registros_bc['data']:
                    dict = self._preparar_diccionario_odoo(registro)
                    # Cada modelo de este módulo de sincronización que llama a este método (transferir_bc_odoo), 
                    # debe tener definido un método llamado res_model() y otro llamado filtro_odoo().
                    obj = self.env[self.res_model()].search(self.filtro_odoo(registro['id']))
                    if not obj:
                        obj = self.env[self._name].create_odoo(dict)
                        if obj:
                            logging.warn('Crear ' + self.res_model() + ': True')
                        else:
                            logging.warn('Crear ' + self.res_model() + ': False')
                    else:
                        if self.env[self._name].write_odoo(dict):
                            logging.warn('Modificar ' + self.res_model() + ': True')
                        else:
                            logging.warn('Modificar ' + self.res_model() + ': False')

                if registros_bc['meta']['pagination']['current_page'] >= registros_bc['meta']['pagination']['total_pages']:
                    seguir = False
                else:
                    pagina += 1
            else:
                seguir = False

    # Prepara el diccionario para crear o modificar registros en BigCommerce.
    def _preparar_diccionario_bc(self, registro):
        dict = {}
        campos = self.campos()
        for campo in campos['clasicos']:
            if len(campo) == 2:
                if not isinstance(campo[1], list) and campo[0] != 'sinc_id':
                    dict[campo[1]] = registro[campo[0]]
        return dict

    # Crea o modifica un registro en BigCommerce.
    def transferir_odoo_bc(self, filtros = None):
        registros = self.obtener_odoo_info(filtros)
        if registros:
            for registro in registros:
                dict = self._preparar_diccionario_bc(registro)
                if not registro.sinc_id or registro.sinc_id == 0:
                    bc_id = self.create_bc(dict)
                    registro.sinc_id = bc_id
                    logging.warn('Crear')
                else:
                    self.write_bc(dict, registro.sinc_id)
                    logging.warn('Modificar')

