#!/usr/bin/env python3
"""Request Wrapper for SENSE-0 API"""
import os
import sys

import logging
from http.client import HTTPConnection
import requests
from sense.client.apiclient import ApiClient

sys.path.insert(0, '..')


class RequestWrapper(ApiClient):
    def __init__(self):
        self.debug = False
        self.__setdebug()
        super(RequestWrapper, self).__init__()

    def __setdebug(self):
        """Set Debug and log all http call details to console"""
        if not os.environ.get('SENSE_FULL_DEBUG'):
            log = logging.getLogger('RequestWrapperSense')
            log.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            if ch in log.handlers:
                log.addHandler(ch)
            self.debug = False
            return
        if not self.debug:
            log = logging.getLogger('RequestWrapperSense')
            log.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            if ch not in log.handlers:
                log.removeHandler(ch)
            HTTPConnection.debuglevel = 1
            self.debug = True

    @staticmethod
    def _getHTTPTimeout():
        """Get HTTP Timeout from env or default to 60 seconds"""
        return int(os.environ.get('SENSE_TIMEOUT', 60))

    def _get(self, api_path, params):
        url = self.config['REST_API'] + api_path
        out = requests.get(url,
                           headers=self.config['headers'],
                           verify=self.config['verify'],
                           params=params, timeout=self._getHTTPTimeout())
        if out.status_code == 401:
            self._refreshToken()
            out = requests.get(url,
                               headers=self.config['headers'],
                               verify=self.config['verify'],
                               params=params, timeout=self._getHTTPTimeout())
        return out

    def _put(self, api_path, data, params):
        url = self.config['REST_API'] + api_path
        out = requests.put(url,
                           headers=self.config['headers'],
                           verify=self.config['verify'],
                           data=data,
                           params=params, timeout=self._getHTTPTimeout())
        if out.status_code == 401:
            self._refreshToken()
            out = requests.put(url,
                               headers=self.config['headers'],
                               verify=self.config['verify'],
                               data=data,
                               params=params, timeout=self._getHTTPTimeout())
        return out

    def _post(self, api_path, data, params):
        url = self.config['REST_API'] + api_path
        out = requests.post(url,
                            headers=self.config['headers'],
                            verify=self.config['verify'],
                            data=data,
                            params=params, timeout=self._getHTTPTimeout())
        if out.status_code == 401:
            self._refreshToken()
            out = requests.post(url,
                                headers=self.config['headers'],
                                verify=self.config['verify'],
                                data=data,
                                params=params, timeout=self._getHTTPTimeout())
        return out

    def _delete(self, api_path, params):
        url = self.config['REST_API'] + api_path
        out = requests.delete(url,
                              headers=self.config['headers'],
                              verify=self.config['verify'],
                              params=params, timeout=self._getHTTPTimeout())
        if out.status_code == 401:
            self._refreshToken()
            out = requests.delete(url,
                                  headers=self.config['headers'],
                                  verify=self.config['verify'],
                                  params=params, timeout=self._getHTTPTimeout())
        return out

    def request(self, call_type, api_path, **kwargs):
        """Request Wrapper for SENSE-0 API (GET, PUT, POST, DELETE)"""
        self.__setdebug()
        ret = None
        params = None
        if kwargs.get('query_params'):
            params = kwargs.get('query_params')

        if call_type == "GET":
            ret = self._get(api_path, params)
        elif call_type == "PUT":
            ret = self._put(api_path, kwargs.get('body_params'), params)
        elif call_type == "POST":
            if kwargs.get('body_params'):
                ret = self._post(api_path, kwargs.get('body_params'), params)
            else:
                raise ValueError(
                    f"Missing the body parameter for POST to '{api_path}'")
        elif call_type == "DELETE":
            ret = self._delete(api_path, params)

        if ret is not None and ret.status_code >= 400 and ret.headers.get("content-type") == "application/json":
            json = ret.json()
            error_message = str(json)
            if "exception" in json:
                error_message = json.get("exception")
            raise ValueError(
                    f"Returned code {ret.status_code} with error '{error_message}'")

        if ret and self.config['headers'].get('Accept') == "application/json" and ret.headers.get("content-type") == "application/json":
            return ret.json()

        return ret.text if ret.text is not None else ret
