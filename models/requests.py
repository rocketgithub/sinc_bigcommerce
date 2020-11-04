# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import time
import math
import logging

class SincRequests(models.AbstractModel):
    _name = 'sinc_bigcommerce.requests'

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

    def _headers_put(self):
        return self._headers_post()

    def _headers_delete(self):
        return self._headers_post()

    def _requests_monitor(self, headers):
#        logging.warn('Requests: ' + headers['X-Rate-Limit-Requests-Left'] + ' --> ' + headers['X-Rate-Limit-Requests-Quota'] + ' --- Time: ' + headers['X-Rate-Limit-Time-Reset-Ms'] + ' --> ' + headers['X-Rate-Limit-Time-Window-Ms'])
        if (int(headers['X-Rate-Limit-Requests-Left']) / int(headers['X-Rate-Limit-Requests-Quota'])) < 0.30:
            pausa = math.ceil(int(headers['X-Rate-Limit-Time-Reset-Ms']) / 1000) + 1
            logging.getLogger('BigCommerce Limit-Requests. Pausa en sincronizacion por').warn(str(pausa) + ' segundos')
            time.sleep(pausa)

    def get(self, url):
        response = requests.get(url, headers=self._headers_get())
        if response.status_code == requests.codes.ok:
            self._requests_monitor(response.headers)
            return response.text
        else:
            logging.getLogger('requests.get ERROR').warn(url)
            return False

    def post(self, url, data):
        response = requests.post(url, data=data, headers=self._headers_post())
        if response.status_code == requests.codes.ok:
            res = response.json()
            self._requests_monitor(response.headers)
            return res['data']['id']
        else:
            logging.warn('ERROR requests.put: ' + response.json()['title'])
            logging.getLogger('data').warn(data)
            return False

    def put(self, url, data):
        response = requests.put(url, data=data, headers=self._headers_put())
        if response.status_code == requests.codes.ok:
            res = response.json()
            self._requests_monitor(response.headers)
            return res['data']['id']
        else:
            logging.warn('ERROR requests.put: ' + response.json()['title'])
            logging.getLogger('data').warn(data)
            return False

    def delete(self, url):
        response = requests.delete(url, headers=self._headers_delete())
#        if response.status_code == requests.codes.ok:
        if response.status_code == 204:
            self._requests_monitor(response.headers)
            return response
        else:
            logging.getLogger('requests.delete ERROR').warn(url)
            return False
