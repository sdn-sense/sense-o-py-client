#!/usr/bin/env python3
# coding: utf-8
# pylint: disable=too-few-public-methods,no-member
"""
    SENSE-SiteRM Base Class for All APIs
"""
from sense.client.siterm.requestwrapper import RequestWrapper

class BaseApi:
    """Base class for all SENSE-SiteRM APIs"""
    def __init__(self):
        self.client = RequestWrapper()

    def getSitename(self, **kwargs):
        """Get sitename from kwargs or urn"""
        sitename = kwargs.get("sitename", None)
        urn = kwargs.get("urn", None)
        if sitename and urn:
            # Check if urn sitename matches sitename
            sitenameFromUrn = self.client.getSitenameFromUrn(urn)
            if sitenameFromUrn != sitename:
                raise Exception(f"Urn {urn} does not match sitename {sitename} (urn should be {sitenameFromUrn})")
        if not sitename and urn:
            sitename = self.client.getSitenameFromUrn(urn)
        if not sitename:
            raise Exception("Sitename is required for API calls (or urn to get sitename dynamically)")
        return sitename
