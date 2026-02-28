#!/usr/bin/env python3
"""API Client for SENSE-0 get Token and Config"""
import os
import json
import requests
from sense.common import classwrapper, getHTTPTimeout
from sense.common import getConfig

requests.packages.urllib3.disable_warnings()


@classwrapper
class ApiClient:
    """API Client for SENSE-0 get Token and Config"""

    def __init__(self, config):
        # For now only pass config file; Later all params
        self.config = config or getConfig()
        self._validateConfig()
        self._setDefaults()
        self.token = None
        self._initAuth()

    def _initAuth(self):
        """
        Initialize auth in this order:
          1) If ACCESS_TOKEN exists, use it.
          2) Else if REFRESH_TOKEN exists, refresh to get a new ACCESS_TOKEN.
          3) Else use USERNAME/PASSWORD to get tokens (last resort).
        """
        access = self.config.get('ACCESS_TOKEN')
        refresh = self.config.get('REFRESH_TOKEN')

        if access:
            self.token = {
                'access_token': access,
                'refresh_token': refresh
            }
            self._setHeaders()
            return

        if refresh:
            # Try to obtain a new access token via refresh-token grant
            self._refreshToken()
            return

        # Last resort: password flow
        self._getToken()

    def _getToken(self):
        """Get Token from SENSE-0 Auth API (password grant)"""
        data = {'grant_type': 'password',
                'username': self.config['USERNAME'],
                'password': self.config['PASSWORD']}
        tokenResponse = requests.post(self.config['AUTH_ENDPOINT'],
                                      data=data,
                                      verify=self.config['verify'],
                                      allow_redirects=self.config['allow_redirects'],
                                      auth=(self.config['CLIENT_ID'], self.config['SECRET']),
                                      timeout=getHTTPTimeout())
        try:
            self.token = json.loads(tokenResponse.text)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to get token. Bad credentials? Error: {tokenResponse.text}")
        if 'error' in self.token.keys() and 'error_description' in self.token.keys():
            raise Exception(f"Failed to get token. Bad credentials? Error: {self.token['error_description']}")

        # Keep tokens in config for runtime use by refresh/init logic
        self.config['ACCESS_TOKEN'] = self.token.get('access_token')
        self.config['REFRESH_TOKEN'] = self.token.get('refresh_token')

        self._setHeaders()

    def _setHeaders(self, content='json', accept='json'):
        """Set Headers for API calls"""
        if not self.token or not self.token.get('access_token'):
            raise Exception("No ACCESS_TOKEN available to set Authorization header")
        self.config['headers'] = {'Content-type': f'application/{content}', 'Accept': f'application/{accept}',
                                  'Authorization': 'Bearer ' + self.token['access_token']}

    def _refreshToken(self):
        """
        Refresh Token from SENSE-0 Auth API.

        If refresh fails:
          - fall back to USERNAME/PASSWORD (if present),
          - otherwise raise an exception.
        """
        refresh_token = None
        if self.token and self.token.get('refresh_token'):
            refresh_token = self.token.get('refresh_token')
        if not refresh_token:
            refresh_token = self.config.get('REFRESH_TOKEN')

        if not refresh_token:
            # No refresh token available; last resort to password flow if possible
            if self.config.get('USERNAME') and self.config.get('PASSWORD'):
                self._getToken()
                return
            raise Exception("No REFRESH_TOKEN available and no USERNAME/PASSWORD configured")

        data = {'grant_type': 'refresh_token',
                'client_id': self.config['CLIENT_ID'],
                'client_secret': self.config['SECRET'],
                'refresh_token': refresh_token}
        tokenResponse = requests.post(self.config['AUTH_ENDPOINT'],
                                      data=data,
                                      verify=self.config['verify'],
                                      allow_redirects=self.config['allow_redirects'],
                                      timeout=getHTTPTimeout())
        self.token = json.loads(tokenResponse.text)

        if 'error' in self.token.keys() and 'error_description' in self.token.keys():
            # Refresh failed -> last resort
            if self.config.get('USERNAME') and self.config.get('PASSWORD'):
                self._getToken()
                return
            raise Exception(f"Failed to refresh token and no USERNAME/PASSWORD configured: {self.token.get('error_description')}")

        # Keep tokens in config for runtime use
        self.config['ACCESS_TOKEN'] = self.token.get('access_token')
        self.config['REFRESH_TOKEN'] = self.token.get('refresh_token', refresh_token)

        self._setHeaders()

    def _setDefaults(self):
        """Set Defaults for Config"""
        for key, val in {'verify': False,
                         'allow_redirects': False,
                         'REST_API': self.config['API_ENDPOINT']}.items():
            if key not in self.config.keys():
                self.config[key] = val

    def _validateConfig(self):
        """Validate Config"""
        # Always required
        for param in ['AUTH_ENDPOINT', 'API_ENDPOINT', 'CLIENT_ID', 'SECRET']:
            if param not in self.config.keys():
                raise Exception(f"Config parameter {param} is not set")

        # Must have at least one auth path configured:
        # - ACCESS_TOKEN, or
        # - REFRESH_TOKEN, or
        # - USERNAME+PASSWORD (last resort)
        has_access = bool(self.config.get('ACCESS_TOKEN'))
        has_refresh = bool(self.config.get('REFRESH_TOKEN'))
        has_userpass = bool(self.config.get('USERNAME')) and bool(self.config.get('PASSWORD'))

        if not (has_access or has_refresh or has_userpass):
            raise Exception("Config must include ACCESS_TOKEN or REFRESH_TOKEN or USERNAME+PASSWORD")
