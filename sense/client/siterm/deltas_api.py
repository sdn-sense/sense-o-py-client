#!/usr/bin/env python3
# coding: utf-8
"""
    SENSE-SiteRM Deltas API
"""
from sense.client.siterm.requestwrapper import RequestWrapper


class DeltasApi:
    """Deltas API for SENSE-SiteRM"""
    def __init__(self):
        self.client = RequestWrapper()

    def _getSitename(self, **kwargs):
        sitename = kwargs.get("sitename", None)
        if not sitename:
            raise Exception("Sitename is required for get_configuration")
        return sitename

    def get_deltas(self, **kwargs):
        """Get deltas from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        for key in ['summary', 'limit']:
            if key in kwargs and kwargs[key]:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                        url=f"/api/{sitename}/deltas",
                                        **{"verb": "GET", "data": {}, "urlparams": kwargs.get('urlparams', None)})

    def get_delta(self, **kwargs):
        """Get delta from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        for key in ['summary']:
            if key in kwargs and kwargs[key]:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                        url=f"/api/{sitename}/deltas/{kwargs.get('delta_id')}",
                                        **{"verb": "GET", "data": {}, "urlparams": kwargs.get('urlparams', None)})

    def get_delta_timestates(self, **kwargs):
        """Get delta time states from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        for key in ['limit']:
            if key in kwargs and kwargs[key]:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                        url=f"/api/{sitename}/deltas/{kwargs.get('delta_id')}/timestates",
                                        **{"verb": "GET", "data": {}, "urlparams": kwargs.get('urlparams', None)})

    def set_delta_action(self, **kwargs):
        """Set delta action in the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        if not ('delta_id' in kwargs and kwargs['delta_id']):
            raise Exception("Delta ID is required to set delta action.")
        if not ('action' in kwargs and kwargs['action']):
            raise Exception("Action is required to set delta action.")
        return self.client.makeRequest(sitename=sitename,
                                        url=f"/api/{sitename}/deltas/{kwargs['delta_id']}/actions/{kwargs['action']}",
                                        **{"verb": "PUT", "data": {}})
