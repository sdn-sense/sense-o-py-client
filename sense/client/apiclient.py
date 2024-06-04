import os
import json
import requests
from yaml import load as yload

requests.packages.urllib3.disable_warnings()

class ApiClient():
    """API Client for SENSE-0 get Token and Config"""
    def __init__(self):
        # For now only pass config file; Later all params
        self.token, self.config = None, None
        self.getConfig()
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

    def _setHeaders(self):
        """Set Headers for API calls"""
        self.config['headers'] = {'Content-type': 'application/json', 'Accept': 'application/json',
                                  'Authorization': 'Bearer ' + self.token['access_token']}

    def _refreshToken(self):
        """Refresh Token from SENSE-0 Auth API"""
        self.getConfig()
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

    def getConfig(self, configFile='/etc/sense-o-auth.yaml'):
        """Get SENSE Auth config file"""
        if os.getenv('SENSE_AUTH_OVERRIDE'):
            configFile = os.getenv('SENSE_AUTH_OVERRIDE')
            if not os.path.isfile(configFile):
                raise Exception(f"SENSE_AUTH_OVERRIDE env flag set, but file not found: {configFile}")
        elif not os.path.isfile(configFile):
            configFile = os.getenv('HOME') + '/.sense-o-auth.yaml'
            if not os.path.isfile(configFile):
                raise Exception(f"Config file not found: {configFile}")
        with open(configFile, 'r', encoding="utf-8") as fd:
            self.config = yload(fd.read())
        self._validateConfig()
        self._setDefaults()
