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

    def findSitename(self, **kwargs):
        """Same as getSitename, but returns None instead of raising when no SiteRM
        owns the urn's network domain.

        For callers that walk a path and ask "is this endpoint one we manage?",
        rather than callers that need a sitename to address a site."""
        urn = kwargs.get("urn", None)
        if urn and self.client.findSitenameFromUrn(urn) is None:
            return kwargs.get("sitename", None)
        return self.getSitename(**kwargs)

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
