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

    def _get_sitename(self, **kwargs):
        sitename = kwargs.get("sitename", None)
        if not sitename:
            raise Exception("Sitename is required for get_configuration")
        return sitename

    # TODO. Need to rewrite with checked Frontend output from debugactioninfo
    # Each Frontend and Site can support different parameters and actions. And also have different defaults.
    #def _validate_input(self, keys, kwargs, action):
    #    """Validate input for debug actions"""
    #    if set(kwargs.keys()) != set(keys):
    #        raise Exception(f"Wrong input for {action}. Must have these keys: {keys}. Input: {kwargs}")


    def get_debugactions(self, **kwargs):
        """Get debug actions from the SENSE-SiteRM API"""
        sitename = self._get_sitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/debugactions",
                                       **{"verb": "GET", "data": {}})

    def get_debugactioninfo(self, **kwargs):
        """Get debug action info from the SENSE-SiteRM API"""
        sitename = self._get_sitename(**kwargs)
        action = kwargs.get("action", None)
        if not action:
            raise Exception("Action is required for get_debugactioninfo")
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/debugactioninfo",
                                       **{"verb": "GET", "data": {}, "urlparams": {"action": action}})


    def __submit_call(self, **kwargs):
        """Submit a debug call to the SENSE-SiteRM API"""
        sitename = self._get_sitename(**kwargs)
        submitout = {"hostname": kwargs.get("hostname", "undefined"),
                     "request": kwargs}
        return self.client.makeRequest(sitename=sitename, url=f"/api/{sitename}/debug",
                                       **{"verb": "POST", "data": submitout})

    def _check_action_supported(self, action, **kwargs):
        """Check if the action is supported by the SENSE-SiteRM instance"""
        actions = self.get_debugactions(**kwargs)
        if action not in actions[0].get("actions", []):
            raise Exception(f"Action {action} is not supported by the {kwargs.get('sitename', None)} instance.")

    def submit(self, **kwargs):
        """Submit a debug action to the SENSE-SiteRM API"""
        action = kwargs.get("action", None)
        if not action:
            raise Exception("Action is required for submit")
        self._check_action_supported(action, **kwargs)
        return self.__submit_call(**kwargs)

    def submit_ping(self, **kwargs):
        """Submit a ping test to the SENSE-SiteRM API"""
        self._check_action_supported("rapid-ping", **kwargs)
        kwargs["type"] = "rapid-ping"
        return self.__submit_call(**kwargs)

    def submit_arptable(self, **kwargs):
        """Submit an ARP table request to the SENSE-SiteRM API"""
        kwargs["type"] = "arp-table"
        return self.__submit_call(**kwargs)

    def submit_tcpdump(self, **kwargs):
        """Submit a tcpdump request to the SENSE-SiteRM API"""
        kwargs["type"] = "tcpdump"
        return self.__submit_call(**kwargs)

    def submit_traceroute(self, **kwargs):
        """Submit a traceroute request to the SENSE-SiteRM API"""
        kwargs["type"] = "traceroute"
        return self.__submit_call(**kwargs)

    def submit_iperfclient(self, **kwargs):
        """Submit an iperf client request to the SENSE-SiteRM API"""
        kwargs["type"] = "iperf-client"
        return self.__submit_call(**kwargs)

    def submit_iperfserver(self, **kwargs):
        """Submit an iperf server request to the SENSE-SiteRM API"""
        kwargs["type"] = "iperf-server"
        return self.__submit_call(**kwargs)

    def submit_arppush(self, **kwargs):
        """Submit an ARP push request to the SENSE-SiteRM API"""
        kwargs["type"] = "arp-push"
        return self.__submit_call(**kwargs)

    def submit_fdtserver(self, **kwargs):
        """Submit an FDT server request to the SENSE-SiteRM API"""
        kwargs["type"] = "fdt-server"
        return self.__submit_call(**kwargs)

    def submit_fdtclient(self, **kwargs):
        """Submit an FDT client request to the SENSE-SiteRM API"""
        kwargs["type"] = "fdt-client"
        return self.__submit_call(**kwargs)

    def submit_ethrserver(self, **kwargs):
        """Submit an ethr server request to the SENSE-SiteRM API"""
        kwargs["type"] = "ethr-server"
        return self.__submit_call(**kwargs)

    def submit_ethrclient(self, **kwargs):
        """Submit an ethr client request to the SENSE-SiteRM API"""
        kwargs["type"] = "ethr-client"
        return self.__submit_call(**kwargs)

    def get_debug(self, **kwargs):
        """Get debug info from SENSE-SiteRM Endpoint"""
        sitename = self._get_sitename(**kwargs)
        urlparams = {}
        for key in ["details", "hostname", "state", "limit"]:
            if key in kwargs and kwargs[key]:
                urlparams[key] = kwargs[key]
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/debug/{kwargs['id']}",
                                       **{"verb": "GET", "urlparams": urlparams})

    def get_all_debug_hostname(self, **kwargs):
        """Get all debug info from SENSE-SiteRM Endpoint"""
        sitename = self._get_sitename(**kwargs)
        params = "?"
        for key in ["hostname", "state", "limit", "action"]:
            if key in kwargs and kwargs[key]:
                params += f"{key}={kwargs[key]}&"
        params += "debugvar=ALL&details=true"
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/debug{params}",
                                       **{"verb": "GET", "data": {}})

    def delete_debug(self, **kwargs):
        """Delete debug info in SENSE-SiteRM Endpoint"""
        sitename = self._get_sitename(**kwargs)
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/debug/{kwargs['id']}",
                                       **{"verb": "DELETE", "data": {}})

    def update_debug(self, **kwargs):
        """Update debug info in SENSE-SiteRM Endpoint"""
        sitename = self._get_sitename(**kwargs)
        if "state" not in kwargs or not kwargs["state"]:
            raise Exception("State is required for update_debug")
        if "id" not in kwargs or not kwargs["id"]:
            raise Exception("ID is required for update_debug")
        data = {"id": kwargs["id"], "state": kwargs["state"]}
        if "output" in kwargs and kwargs["output"]:
            data["output"] = kwargs["output"]
        return self.client.makeRequest(sitename=sitename,
                                       url=f"/api/{sitename}/debug/{kwargs['id']}",
                                       **{"verb": "PUT", "data": data})
