# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import logging

class SincRequests(models.AbstractModel):
    _name = 'sinc_bigcommerce.requests'

    # Retorna los headers que se utilizarán en el get request.
    def _headers_get(self):
        headers = {
            'Accept': 'application/json',
            'cache-control': 'no-cache',
            'X-Auth-Client': self.env["res.config.settings"].obtener_client_id(),
            'X-Auth-Token': self.env["res.config.settings"].obtener_access_token()
        }
        return headers

    def _headers_post(self):
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'x-auth-client': self.env["res.config.settings"].obtener_client_id(),
            'x-auth-token': self.env["res.config.settings"].obtener_access_token()
        }
        return headers

    def get(self, url):
        response = requests.get(url, headers=self._headers_get())
        if response.status_code == requests.codes.ok:
            return response.text
        else:
            return False

    def post(self, url, data):
        logging.warn(url)
        logging.warn(data)
        response = requests.post(url, data=data, headers=self._headers_post())
        logging.getLogger('response').warn(response)
        logging.getLogger('response.text').warn(response.text)
        if response.status_code == requests.codes.ok:
            res = response.json()
            logging.getLogger('response.json').warn(res)
            return res['data']['id']
        else:
            return False

    def put(self, url, data):
        response = requests.put(url, data=data, headers=self._headers_post())
        if response.status_code == requests.codes.ok:
            res = response.json()
            logging.getLogger('response.json').warn(res)
            return res['data']['id']
        else:
            return False

    def delete(self, url):
        logging.getLogger('delete url').warn(url)
        response = requests.delete(url)
        logging.getLogger('response 1').warn(response)
        if response.status_code == requests.codes.ok:
            return response
        else:
            return False
