#!/usr/bin/env python3
"""
Title                   : siterm-api
Author                  : Justas Balcas
Email                   : jbalcas (at) es.net
@Copyright              : Copyright (C) 2024 ESnet
Date                    : 2024/06/05
"""
import os
import tempfile
from shutil import rmtree
import datetime
import json
import requests
import urllib3
from git import Repo
from sense.common import classwrapper
from sense.common import getConfig
from sense.common import loadYamlFile
from sense.common import getHTTPTimeout

@classwrapper
class GitRepo():
    """Git Repo Class for SENSE-SiteRM API to get all endpoints for sites"""
    def __init__(self, config):
        self.config = config

    def _getSiteRMRepo(self):
        """Get SiteRM Config Repo"""
        dirPath = tempfile.mkdtemp()
        Repo.clone_from(self.config['SITERM_REPO'], dirPath)
        return dirPath

    def getAllSiteRMs(self):
        """Get All SiteRM Configs"""
        fname = f"/tmp/siterm_endpoints_cache_{datetime.datetime.now().strftime('%Y-%m-%d')}.json"
        siteUrls = {}
        if os.path.isfile(fname):
            with open(fname, 'r', encoding="utf-8") as fd:
                return json.loads(fd.read())
        # If cache file not available, prepare a new one.
        repo = self._getSiteRMRepo()
        for dirName in os.listdir(repo):
            siteConfDir = os.path.join(repo, dirName)
            mappingFile = os.path.join(siteConfDir, 'mapping.yaml')
            if not os.path.isfile(mappingFile):
                continue
            mapping = loadYamlFile(mappingFile)
            for _key, val in mapping.items():
                if val.get('type', '') == 'FE' and val.get('config', ''):
                    tmpD = os.path.join(siteConfDir, val.get('config'))
                    confFile = os.path.join(tmpD, 'main.yaml')
                    if not os.path.isfile(confFile):
                        continue
                    conf = loadYamlFile(confFile)
                    webdomain = conf.get('general', {}).get('webdomain', '')
                    for site in conf.get('general', {}).get('sites', ''):
                        siteUrls.setdefault(site, webdomain)
        # Remove dir
        rmtree(repo, ignore_errors=True)
        # Save to cache file
        with open(fname, 'w', encoding="utf-8") as fd:
            fd.write(json.dumps(siteUrls))
        return siteUrls

@classwrapper
class RequestWrapper(GitRepo):
    """Request Wrapper for SENSE-SiteRM API"""
    def __init__(self):
        self.config = getConfig()
        self._setDefaults()
        self._validateConfig()
        self.cert = (self.config['SITERM_CERT'], self.config['SITERM_KEY'])
        if not self.config['SITERM_VERIFY']:
            urllib3.disable_warnings()
        super(RequestWrapper, self).__init__(self.config)
        self.fes = self.getAllSiteRMs()

    def _setDefaults(self):
        """Set Defaults for Config"""
        for key, val in {'SITERM_REPO': 'https://github.com/sdn-sense/rm-configs',
                         'SITERM_CERT': '/etc/grid-security/hostcert.pem',
                         'SITERM_KEY': '/etc/grid-security/hostkey.pem',
                         'SITERM_VERIFY': False}.items():
            if key not in self.config.keys():
                self.config[key] = val

    def _validateConfig(self):
        """Validate Config"""
        for param in ['SITERM_REPO', 'SITERM_CERT', 'SITERM_KEY', 'SITERM_VERIFY']:
            if param not in self.config.keys():
                raise Exception(f"Config parameter {param} is not set")

    def _getFullUrl(self, sitename, url):
        """Get Full URL"""
        if sitename not in self.fes.keys():
            raise Exception(f"Sitename {sitename} not found in SiteRM configs")
        urlmain = self.fes[sitename].rstrip('/')
        return f"{urlmain}/{url.lstrip('/')}"

    def makeRequest(self, sitename, url, **kwargs):
        """Make HTTP Request"""
        url = self._getFullUrl(sitename, url)
        if kwargs.get('verb', None) not in ['GET', 'POST', 'PUT']:
            raise Exception(f"Wrong action call {kwargs}")
        # GET
        if kwargs.get('verb') == 'GET':
            out = requests.get(url, cert=self.cert, params=kwargs.get('urlparams', None),
                               verify=self.config['SITERM_VERIFY'], timeout=getHTTPTimeout())
        # POST
        elif kwargs.get('verb') == 'POST':
            out = requests.post(url, cert=self.cert, json=kwargs.get('data', {}),
                                params=kwargs.get('urlparams', None),
                                verify=self.config['SITERM_VERIFY'], timeout=getHTTPTimeout())
        # PUT
        elif kwargs.get('verb') == 'PUT':
            out = requests.put(url, cert=self.cert, json=kwargs.get('data', {}),
                               params=kwargs.get('urlparams', None),
                               verify=self.config['SITERM_VERIFY'], timeout=getHTTPTimeout())
        outval = ""
        try:
            if out.headers.get("content-type") == "application/json":
                outval = out.json()
        except:
            outval = out.text


        return outval, out.ok, out
