#!/usr/bin/env python3
# coding: utf-8
"""
    SENSE-SiteRM Models API
"""
from sense.client.siterm.base_api import BaseApi

class ModelsApi(BaseApi):
    """Models API for SENSE-SiteRM"""
    def __init__(self):
        super().__init__()

    def get_models(self, **kwargs):
        """Get models from the SENSE-SiteRM API"""
        sitename = self.getSitename(**kwargs)
        for key in ['encode', 'summary', 'current', 'limit', 'rdfformat']:
            if key in kwargs and kwargs[key]:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                        url=f"api/{sitename}/models",
                                        **{"verb": "GET", "data": {}, "urlparams": kwargs.get('urlparams', None)})

    def get_model(self, **kwargs):
        """Get model from the SENSE-SiteRM API"""
        sitename = self.getSitename(**kwargs)
        for key in ['encode', 'summary', 'rdfformat']:
            if key in kwargs and kwargs[key]:
                kwargs.setdefault('urlparams', {})
                kwargs['urlparams'][key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                        url=f"/api/{sitename}/models/{kwargs.get('model_id')}",
                                        **{"verb": "GET", "data": {}, "urlparams": kwargs.get('urlparams', None)})
