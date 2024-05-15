import os
import json
import requests
from yaml import load as yload
from yaml import FullLoader

requests.packages.urllib3.disable_warnings()

class ApiClient(object):
    def __init__(self):
        # For now only pass config file; Later all params
        self.token, self.config = None, None
        self.getConfig()
        self._getToken()
        pass

    def _getToken(self):
        data = {'grant_type': 'password',
                'username': self.config['USERNAME'],
                'password': self.config['PASSWORD']}
        tokenResponse = requests.post(self.config['AUTH_ENDPOINT'],
                                      data=data,
                                      verify=self.config['verify'],
                                      allow_redirects=self.config['allow_redirects'],
                                      auth=(self.config['CLIENT_ID'], self.config['SECRET']))
        self.token = json.loads(tokenResponse.text)
        if 'error' in self.token.keys() and 'error_description' in self.token.keys():
            raise Exception("Failed to get token. Bad credentials? Error: %s" % self.token['error_description'])
        self._setHeaders()

    def _setHeaders(self):
        self.config['headers'] = {'Content-type': 'application/json', 'Accept': 'application/json',
                                  'Authorization': 'Bearer ' + self.token['access_token']}

    def _refreshToken(self):
        self.getConfig()
        self._getToken()

    def _setDefaults(self):
        for key, val in {'verify': False,
                         'allow_redirects': False,
                         'REST_API': self.config['API_ENDPOINT']}.items():
            if key not in self.config.keys():
                self.config[key] = val

    def _validateConfig(self):
        for param in ['AUTH_ENDPOINT', 'API_ENDPOINT', 'USERNAME', 'PASSWORD', 'CLIENT_ID', 'SECRET']:
            if param not in self.config.keys():
                raise Exception('Config parameter %s is not set' % param)

    def getConfig(self, configFile='/etc/sense-o-auth.yaml'):
        """Get SENSE Auth config file"""
        if os.getenv('SENSE_AUTH_OVERRIDE'):
            configFile = os.getenv('SENSE_AUTH_OVERRIDE')
            if not os.path.isfile(configFile):
                raise Exception('SENSE_AUTH_OVERRIDE env flag set, but file not found: %s' % configFile)
        elif not os.path.isfile(configFile):
            configFile = os.getenv('HOME') + '/.sense-o-auth.yaml'
            if not os.path.isfile(configFile):
                raise Exception('Config file not found: %s' % configFile)
        with open(configFile, 'r') as fd:
            self.config = yload(fd.read(), Loader=FullLoader)
        self._validateConfig()
        self._setDefaults()
