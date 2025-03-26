#!/usr/bin/env python3
# coding: utf-8
"""
    SENSE-SiteRM Debug API
"""
from sense.client.siterm.requestwrapper import RequestWrapper


class DebugApi:
    """Debug API for SENSE-SiteRM"""
    def __init__(self):
        self.client = RequestWrapper()

    def _validate_input(self, keys, kwargs, action):
        """Validate input for debug actions"""
        sitename = kwargs.get("sitename", None)
        if not sitename:
            raise Exception(f"Sitename is required for {action} test")
        if set(kwargs.keys()) != set(keys):
            raise Exception(f"Wrong input for {action}. Must have these keys: {keys}. Input: {kwargs}")
        return sitename

    def __submit_call(self, keys, **kwargs):
        """Submit a debug call to the SENSE-SiteRM API"""
        sitename = self._validate_input(keys, kwargs, kwargs.get("type"))

        return self.client.makeRequest(sitename=sitename, url=f"{kwargs['sitename']}/sitefe/json/frontend/submitdebug/NEW",
                                       **{"verb": "POST", "data": kwargs})

    def submit_ping(self, **kwargs):
        """Submit a ping test to the SENSE-SiteRM API"""
        keys = ["hostname", "type", "sitename", "ip",
                "packetsize", "interval", "interface", "time", "onetime"]
        kwargs["type"] = "rapid-ping"  # Default to rapid-ping
        return self.__submit_call(keys, **kwargs)

    def submit_arptable(self, **kwargs):
        """Submit an ARP table request to the SENSE-SiteRM API"""
        keys = ["hostname", "type", "sitename", "interface"]
        kwargs["type"] = "arp-table"  # Default to arp-table
        return self.__submit_call(keys, **kwargs)

    def submit_tcpdump(self, **kwargs):
        """Submit a tcpdump request to the SENSE-SiteRM API"""
        keys = ["hostname", "type", "sitename", "interface"]
        kwargs["type"] = "tcpdump"  # Default to tcpdump
        return self.__submit_call(keys, **kwargs)

    def submit_traceroute(self, **kwargs):
        """Submit a traceroute request to the SENSE-SiteRM API"""
        keys = ["hostname", "type", "sitename", "ip", "from_ip", "from_interface"]
        kwargs["type"] = "traceroute"  # Default to traceroute
        return self.__submit_call(keys, **kwargs)

    def submit_iperfclient(self, **kwargs):
        """Submit an iperf client request to the SENSE-SiteRM API"""
        keys = ["hostname", "type", "sitename", "interface", "ip", "port", "time"]
        kwargs["type"] = "iperf-client"  # Default to iperf-client
        return self.__submit_call(keys, **kwargs)

    def submit_iperfserver(self, **kwargs):
        """Submit an iperf server request to the SENSE-SiteRM API"""
        keys = ["hostname", "type", "sitename", "interface", "port", "time", "onetime", "ip"]
        kwargs["type"] = "iperf-server"  # Default to iperf-server
        return self.__submit_call(keys, **kwargs)

    def submit_prompush(self, **kwargs):
        """Submit a prometheus push request to the SENSE-SiteRM API"""
        keys = ["hostname", "hosttype", "type", "sitename", "gateway", "runtime", "resolution", "metadata"]
        kwargs["type"] = "prometheus-push"  # Default to prometheus-push
        return self.__submit_call(keys, **kwargs)

    def submit_arppush(self, **kwargs):
        """Submit an ARP push request to the SENSE-SiteRM API"""
        keys = ["hostname", "hosttype", "type", "sitename", "gateway", "runtime", "resolution", "metadata"]
        kwargs["type"] = "arp-push"  # Default to prometheus-push
        return self.__submit_call(keys, **kwargs)


    def get_debug(self, **kwargs):
        """Get debug info from SENSE-SiteRM Endpoint"""
        sitename = self._validate_input(["sitename", "id"], kwargs, "get-debug")
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/{sitename}/sitefe/json/frontend/getdebug/{kwargs['id']}",
                                       **{"verb": "GET", "data": {}})

    def get_all_debug_hostname(self, **kwargs):
        """Get all debug info from SENSE-SiteRM Endpoint"""
        sitename = self._validate_input(["sitename", "hostname", "state"], kwargs, "get-all-debug")
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/{sitename}/sitefe/json/frontend/getalldebughostname/{kwargs['hostname']}/{kwargs['state']}",
                                       **{"verb": "GET", "data": {}})

    def delete_debug(self, **kwargs):
        """Delete debug info in SENSE-SiteRM Endpoint"""
        sitename = self._validate_input(["sitename", "id"], kwargs, "delete-debug")
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/{sitename}/sitefe/json/frontend/deletedebug/{kwargs['id']}",
                                       **{"verb": "DELETE", "data": {}})
