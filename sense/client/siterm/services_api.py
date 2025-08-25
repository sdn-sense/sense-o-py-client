#!/usr/bin/env python3
# coding: utf-8
"""
    SENSE-SiteRM Services API
"""
from sense.client.siterm.requestwrapper import RequestWrapper


class ServicesApi:
    """Services API for SENSE-SiteRM"""
    def __init__(self):
        self.client = RequestWrapper()

    def _getSitename(self, **kwargs):
        sitename = kwargs.get("sitename", None)
        if not sitename:
            raise Exception("Sitename is required for get_configuration")
        return sitename

    def get_services(self, **kwargs):
        """Get services from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        for key in ['hostname', 'servicename']:
            if key in kwargs:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/services",
                                       **{"verb": "GET", "data": {}, "urlparams": kwargs.get('urlparams', None)})

    def get_servicestates(self, **kwargs):
        """Get service states from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        for key in ['limit']:
            if key in kwargs:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/servicesstates",
                                       **{"verb": "GET", "data": {}, "urlparams": kwargs.get('urlparams', None)})

    def reloadconfig(self, **kwargs):
        """Reload configuration via SENSE-SiteRM API for specific entry"""
        sitename = self._getSitename(**kwargs)
        vals = {"hostname": "default", "servicename": "ALL",
                "sitename": sitename, "action": "reload"}
        for key in vals:
            if key in kwargs:
                vals[key] = kwargs[key]
            if not vals[key]:
                raise Exception(f"Key {key} is required for reloadconfig")
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/serviceaction",
                                       **{"verb": "POST", "data": vals})
