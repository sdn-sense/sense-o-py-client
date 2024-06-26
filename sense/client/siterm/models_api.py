#!/usr/bin/env python3
# coding: utf-8
"""
    SENSE-SiteRM Models API
"""
from sense.client.siterm.requestwrapper import RequestWrapper


class ModelsApi:
    """Models API for SENSE-SiteRM"""
    def __init__(self):
        self.client = RequestWrapper()

    def _getSitename(self, **kwargs):
        sitename = kwargs.get("sitename", None)
        if not sitename:
            raise Exception("Sitename is required for get_configuration")
        return sitename

    def get_models(self, **kwargs):
        """Get models from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        # kwargs['urlparams'] = {'encode': 'false', 'summary': 'false', 'oldview': 'true',
        #                        'current': 'False', 'model': 'turtle'}
        for key in ['encode', 'summary', 'oldview', 'current', 'model']:
            if key in kwargs:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                        url=f"/{sitename}/sitefe/v1/models",
                                        **{"verb": "GET", "data": {}, "urlparams": kwargs.get('urlparams', None)})

    def get_model(self, **kwargs):
        """Get model from the SENSE-SiteRM API"""
        sitename = self._getSitename(**kwargs)
        # kwargs['urlparams'] = {'encode': 'false', 'summary': 'false'}
        for key in ['encode', 'summary']:
            if key in kwargs:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                        url=f"/{sitename}/sitefe/v1/models/{kwargs.get('model_id')}",
                                        **{"verb": "GET", "data": {}})
