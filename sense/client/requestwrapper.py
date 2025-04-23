#!/usr/bin/env python3
"""Request Wrapper for SENSE-0 API"""
import sys

import logging
from http.client import HTTPConnection
import requests
from sense.client.apiclient import ApiClient
from sense.common import isDebugSet
from sense.common import getHTTPTimeout
from sense.common import getHTTPRetries
from sense.common import classwrapper

sys.path.insert(0, '..')


@classwrapper
class RequestWrapper(ApiClient):
    """Request Wrapper for SENSE-0 API (GET, PUT, POST, DELETE)"""
    def __init__(self, config=None):
        self.logger = None
        self.__setdebug()
        super(RequestWrapper, self).__init__(config)

    def __setdebug(self):
        """Set Debug and log all http call details to console"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
            datefmt="%a, %d %b %Y %H:%M:%S",
        )
        handler.setFormatter(formatter)

        logLevel = logging.INFO
        if isDebugSet():
            logLevel = logging.DEBUG
            HTTPConnection.debuglevel = 1

        self.logger = logging.getLogger('RequestWrapperSense')
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logLevel)


    def _get(self, api_path, params):
        url = self.config['REST_API'] + api_path
        out = requests.get(url,
                           headers=self.config['headers'],
                           verify=self.config['verify'],
                           params=params, timeout=getHTTPTimeout())
        if out.status_code == 401:
            self._refreshToken()
            out = requests.get(url,
                               headers=self.config['headers'],
                               verify=self.config['verify'],
                               params=params, timeout=getHTTPTimeout())
        return out

    def _put(self, api_path, data, params):
        url = self.config['REST_API'] + api_path
        out = requests.put(url,
                           headers=self.config['headers'],
                           verify=self.config['verify'],
                           data=data,
                           params=params, timeout=getHTTPTimeout())
        if out.status_code == 401:
            self._refreshToken()
            out = requests.put(url,
                               headers=self.config['headers'],
                               verify=self.config['verify'],
                               data=data,
                               params=params, timeout=getHTTPTimeout())
        return out

    def _post(self, api_path, data, params):
        url = self.config['REST_API'] + api_path
        out = requests.post(url,
                            headers=self.config['headers'],
                            verify=self.config['verify'],
                            data=data,
                            params=params, timeout=getHTTPTimeout())
        if out.status_code == 401:
            self._refreshToken()
            out = requests.post(url,
                                headers=self.config['headers'],
                                verify=self.config['verify'],
                                data=data,
                                params=params, timeout=getHTTPTimeout())
        return out

    def _delete(self, api_path, params):
        url = self.config['REST_API'] + api_path
        out = requests.delete(url,
                              headers=self.config['headers'],
                              verify=self.config['verify'],
                              params=params, timeout=getHTTPTimeout())
        if out.status_code == 401:
            self._refreshToken()
            out = requests.delete(url,
                                  headers=self.config['headers'],
                                  verify=self.config['verify'],
                                  params=params, timeout=getHTTPTimeout())
        return out

    def _requestwrap(self, call_type, api_path, **kwargs):
        """"""
        self.__setdebug()
        ret = None
        params = {}
        if kwargs.get('query_params'):
            params = kwargs.get('query_params')
        retries = getHTTPRetries()
        while retries > 0:
            try:
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
            except requests.exceptions.ReadTimeout as ex:
                self.logger.error(f"Got ReadTimeout exception: {ex}. Retrying up to {retries} times")
                retries -= 1
                continue
            break
        return ret


    def request(self, call_type, api_path, **kwargs):
        """Request Wrapper for SENSE-0 API (GET, PUT, POST, DELETE)"""
        if 'content_type' in kwargs or 'accept_type' in kwargs:
            self._setHeaders(content=kwargs.get('content_type', 'json'), accept=kwargs.get('accept_type', 'json'))

        ret = self._requestwrap(call_type, api_path, **kwargs)

        if ret is not None and ret.status_code >= 400 and ret.headers.get("content-type") == "application/json":
            json = ret.json()
            exc = ValueError(f"Returned code {ret.status_code} with error {json.get('exception')}. Full json return: {str(json)}")
            exc.json = json
            raise exc

        # If request headers and return headers are json, return json
        # In case of failure - return text. Reason for doing so is to
        # avoid issue of diff interpretation of json in java and python
        # e.g. Java API will return str inside quotes (which is valid json based on RFC),
        # but python (or atleast requests) will return str without quotes.
        try:
            if ret and self.config['headers'].get('Accept') == "application/json" and ret.headers.get("content-type") == "application/json":
                return ret.json()
            if ret and self.config['headers'].get('Accept') == "application/xml" and ret.headers.get("content-type") == "application/xml":
                return ret.text  # TODO: valudate XML in ret text
        except:
            pass
        return ret.text if ret.text is not None else ret
