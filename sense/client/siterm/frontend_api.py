#!/usr/bin/env python3
# coding: utf-8
"""
    SENSE-SiteRM Frontend API
"""
from sense.client.siterm.requestwrapper import RequestWrapper


class FrontendApi:
    """Frontend API for SENSE-SiteRM"""
    def __init__(self):
        self.client = RequestWrapper()

    def _getSitename(self, **kwargs):
        sitename = kwargs.get("sitename", None)
        if not sitename:
            raise Exception("Sitename is required for get_configuration")
        return sitename

    def get_alive(self, **kwargs):
        """Get alive status from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url="/api/alive",
                                       **{"verb": "GET", "data": {}})

    def get_ready(self, **kwargs):
        """Get ready status from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url="/api/ready",
                                       **{"verb": "GET", "data": {}})

    def get_liveness(self, **kwargs):
        """Get liveness status from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url="/api/liveness",
                                       **{"verb": "GET", "data": {}})

    def get_readiness(self, **kwargs):
        """Get readiness status from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url="/api/readiness",
                                       **{"verb": "GET", "data": {}})

    def get_sitename(self, **kwargs):
        """Get sitename from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url="/api/frontend/sitename",
                                       **{"verb": "GET", "data": {}})

    def get_configuration(self, **kwargs):
        """Get configuration from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url="/api/frontend/configuration",
                                       **{"verb": "GET", "data": {}})

    def get_switchdata(self, **kwargs):
        """Get switch data from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/frontend/getswitchdata",
                                       **{"verb": "GET", "data": {}})

    def get_activedeltas(self, **kwargs):
        """Get active deltas from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url="/api/frontend/activedeltas",
                                       **{"verb": "GET", "data": {}})

    def get_qosdata(self, **kwargs):
        """Get QoS data from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/frontend/qosdata",
                                       **{"verb": "GET", "data": {}})

    def get_topology(self, **kwargs):
        """Get topology from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/topo/gettopology",
                                       **{"verb": "GET", "data": {}})

    def get_hostdata(self, **kwargs):
        """Get host data from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/hosts",
                                       **{"verb": "GET", "data": {}})