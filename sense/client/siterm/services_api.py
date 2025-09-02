#!/usr/bin/env python3
# coding: utf-8
"""
    SENSE-SiteRM Services API
"""
from sense.client.siterm.base_api import BaseApi

class ServicesApi(BaseApi):
    """Services API for SENSE-SiteRM"""
    def __init__(self):
        super().__init__()

    def get_services(self, **kwargs):
        """Get services from the SENSE-SiteRM API"""
        sitename = self.getSitename(**kwargs)
        for key in ['hostname', 'servicename']:
            if key in kwargs and kwargs[key]:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/services",
                                       **{"verb": "GET", "data": {}, "urlparams": kwargs.get('urlparams', None)})

    def get_servicestates(self, **kwargs):
        """Get service states from the SENSE-SiteRM API"""
        sitename = self.getSitename(**kwargs)
        for key in ['limit']:
            if key in kwargs and kwargs[key]:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/servicesstates",
                                       **{"verb": "GET", "data": {}, "urlparams": kwargs.get('urlparams', None)})

    def reloadconfig(self, **kwargs):
        """Reload configuration via SENSE-SiteRM API for specific entry"""
        sitename = self.getSitename(**kwargs)
        vals = {"hostname": "default", "servicename": "ALL",
                "sitename": sitename, "action": "reload"}
        for key in vals:
            if key in kwargs and kwargs[key]:
                vals[key] = kwargs[key]
            if not vals.get(key):
                raise Exception(f"Key {key} is required for reloadconfig")
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/serviceaction",
                                       **{"verb": "POST", "data": vals})
