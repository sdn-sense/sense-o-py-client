#!/usr/bin/env python3
"""API Client for SENSE-0 get Token and Config"""
import os
import json
import requests
from sense.common import classwrapper
from sense.common import getConfig

requests.packages.urllib3.disable_warnings()

@classwrapper
class ApiClient():
    """API Client for SENSE-0 get Token and Config"""
    def __init__(self, config):
        # For now only pass config file; Later all params
        self.config = config or getConfig()
        self._validateConfig()
        self._setDefaults()
        self.token = None
        self._getToken()

    def _getToken(self):
        """Get Token from SENSE-0 Auth API"""
        data = {'grant_type': 'password',
                'username': self.config['USERNAME'],
                'password': self.config['PASSWORD']}
        tokenResponse = requests.post(self.config['AUTH_ENDPOINT'],
                                      data=data,
                                      verify=self.config['verify'],
                                      allow_redirects=self.config['allow_redirects'],
                                      auth=(self.config['CLIENT_ID'], self.config['SECRET']),
                                      timeout=int(os.environ.get('SENSE_TIMEOUT', 60)))
        self.token = json.loads(tokenResponse.text)
        if 'error' in self.token.keys() and 'error_description' in self.token.keys():
            raise Exception(f"Failed to get token. Bad credentials? Error: {self.token['error_description']}")
        self._setHeaders()

    def _setHeaders(self, content='json', accept='json'):
        """Set Headers for API calls"""
        self.config['headers'] = {'Content-type': f'application/{content}', 'Accept': f'application/{accept}',
                                  'Authorization': 'Bearer ' + self.token['access_token']}

    def _refreshToken(self):
        """Refresh Token from SENSE-0 Auth API"""
        self._getToken()

    def _setDefaults(self):
        """Set Defaults for Config"""
        for key, val in {'verify': False,
                         'allow_redirects': False,
                         'REST_API': self.config['API_ENDPOINT']}.items():
            if key not in self.config.keys():
                self.config[key] = val

    def _validateConfig(self):
        """Validate Config"""
        for param in ['AUTH_ENDPOINT', 'API_ENDPOINT', 'USERNAME', 'PASSWORD', 'CLIENT_ID', 'SECRET']:
            if param not in self.config.keys():
                raise Exception(f"Config parameter {param} is not set")
