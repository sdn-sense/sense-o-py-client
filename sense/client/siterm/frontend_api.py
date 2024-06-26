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

    def get_configuration(self, **kwargs):
        """Get configuration from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/{sitename}/sitefe/json/frontend/configuration",
                                       **{"verb": "GET", "data": {}})

    def get_hostdata(self, **kwargs):
        """Get host data from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/{sitename}/sitefe/json/frontend/gethosts",
                                       **{"verb": "GET", "data": {}})

    def get_switchdata(self, **kwargs):
        """Get switch data from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/{sitename}/sitefe/json/frontend/getswitchdata",
                                       **{"verb": "GET", "data": {}})

    def get_topology(self, **kwargs):
        """Get topology from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/{sitename}/sitefe/json/topo/gettopology",
                                       **{"verb": "GET", "data": {}})

    def get_activedeltas(self, **kwargs):
        """Get active deltas from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/{sitename}/sitefe/json/frontend/getactivedeltas",
                                       **{"verb": "GET", "data": {}})

    def get_qosdata(self, **kwargs):
        """Get QoS data from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"{sitename}/sitefe/json/frontend/getqosdata",
                                       **{"verb": "GET", "data": {}})

    def get_metrics(self, **kwargs):
        """Get metrics from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"{sitename}/sitefe/json/frontend/metrics",
                                       **{"verb": "GET", "data": {}})
