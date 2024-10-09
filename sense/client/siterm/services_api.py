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

    def get_servicestates(self, **kwargs):
        """Get service states from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/{sitename}/sitefe/json/frontend/getservicestates",
                                       **{"verb": "GET", "data": {}})

    def reloadconfig(self, **kwargs):
        """Reload configuration via SENSE-SiteRM API for specific entry"""
        vals = {"hostname": None, "servicename": "ALL",
                "sitename": None, "action": "reload"}
        for key in vals:
            if key in kwargs:
                vals[key] = kwargs[key]
            if not vals[key]:
                raise Exception(f"Key {key} is required for reloadconfig")
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/{sitename}/sitefe/json/frontend/serviceaction",
                                       **{"verb": "POST", "data": vals})
