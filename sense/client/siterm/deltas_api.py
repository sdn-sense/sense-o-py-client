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
        # kwargs['urlparams'] = {'encode': 'false', 'summary': 'false', 'oldview': 'true', 'model': 'turtle'}
        for key in ['encode', 'summary', 'oldview', 'model']:
            if key in kwargs:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                        url=f"/{sitename}/sitefe/v1/deltas",
                                        **{"verb": "GET", "data": {}, "urlparams": kwargs.get('urlparams', None)})

    def get_delta(self, **kwargs):
        """Get delta from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        for key in ['encode', 'summary', 'oldview', 'model']:
            if key in kwargs:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        # kwargs['urlparams'] = {'encode': 'false', 'summary': 'false', 'oldview': 'true', 'model': 'turtle'}
        return self.client.makeRequest(sitename=sitename,
                                        url=f"/{sitename}/sitefe/v1/deltas/{kwargs.get('delta_id')}",
                                        **{"verb": "GET", "data": {}, "urlparams": kwargs.get('urlparams', None)})

    def get_delta_states(self, **kwargs):
        """Get delta states from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                        url=f"/{sitename}/sitefe/v1/deltastates/{kwargs.get('delta_id')}",
                                        **{"verb": "GET", "data": {}})


    def forceapplydelta(self, **kwargs):
        """Force Apply Delta inside SiteRM"""
        sitename = self._getSitename(**kwargs)
        if not ('uuid' in kwargs and kwargs['uuid']):
            raise Exception("Force apply requires delta uuid to be passed as argument.")
        return self.client.makeRequest(sitename=sitename,
                                        url=f"/{sitename}/sitefe/v1/deltaforceapply",
                                        **{"verb": "POST", "data": {"uuid": kwargs["uuid"]}})
