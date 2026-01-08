#!/usr/bin/env python3
"""
Title                   : siterm-api
Author                  : Justas Balcas
Email                   : jbalcas (at) es.net
@Copyright              : Copyright (C) 2024 ESnet
Date                    : 2024/06/05
"""

import os
import json
import base64
import datetime
import tempfile
from pathlib import Path
from shutil import rmtree
from typing import Dict
import httpx
import requests
import urllib3
from git import Repo

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from sense.common import classwrapper
from sense.common import getConfig
from sense.common import loadYamlFile
from sense.common import getHTTPTimeout


# ---------------------------------------------------------
# helpers
# ---------------------------------------------------------

def utcnow():
    """Return the current UTC time as a Unix timestamp."""
    return int(datetime.datetime.utcnow().timestamp())


def sign_challenge(challenge_b64: str, private_key_pem: bytes) -> str:
    """
    Sign base64-encoded challenge using RSA or EC private key.
    """
    challenge = base64.b64decode(challenge_b64)
    key = load_pem_private_key(private_key_pem, password=None)

    if isinstance(key, rsa.RSAPrivateKey):
        signature = key.sign(
            challenge,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    elif isinstance(key, ec.EllipticCurvePrivateKey):
        signature = key.sign(
            challenge,
            ec.ECDSA(hashes.SHA256()),
        )
    else:
        raise RuntimeError("Unsupported private key type")

    return base64.b64encode(signature).decode("utf-8")


# Auth cache file per user
AUTH_CACHE_FILE = os.path.expanduser("~/.siterm/auth.json")

# ---------------------------------------------------------
# GitRepo
# ---------------------------------------------------------

@classwrapper
class GitRepo():
    """Git Repo Class for SENSE-SiteRM API to get all endpoints for sites"""
    def __init__(self, config):
        self.config = config

    def getSiteRMRepo(self):
        """Get SiteRM Config Repo"""
        dirPath = tempfile.mkdtemp()
        Repo.clone_from(self.config.get("SITERM_REPO", "https://github.com/sdn-sense/rm-configs"), dirPath)
        return dirPath

    def getAllSiteRMs(self):
        """Get All SiteRM Configs"""
        fname = os.path.expanduser(f"~/.siterm/siterm_endpoints_cache_{datetime.datetime.now().strftime('%Y-%m-%d')}.json")
        siteUrls = {}
        domainUrns = {}
        if os.path.isfile(fname):
            with open(fname, 'r', encoding="utf-8") as fd:
                tmpdata = json.loads(fd.read())
                return tmpdata.get('fes', {}), tmpdata.get('domainUrns', {})
        # If cache file not available, prepare a new one.
        repo = self.getSiteRMRepo()
        for dirName in os.listdir(repo):
            siteConfDir = os.path.join(repo, dirName)
            mappingFile = os.path.join(siteConfDir, 'mapping.yaml')
            if not os.path.isfile(mappingFile):
                continue
            mapping = loadYamlFile(mappingFile)
            for _key, val in mapping.items():
                if val.get('type', '') == 'FE' and val.get('config', ''):
                    tmpD = os.path.join(siteConfDir, val.get('config'))
                    confFile = os.path.join(tmpD, 'main.yaml')
                    if not os.path.isfile(confFile):
                        continue
                    conf = loadYamlFile(confFile)
                    webdomain = conf.get('general', {}).get('webdomain', '')
                    sitename = conf.get('general', {}).get('sitename', '')
                    siteUrls.setdefault(sitename, webdomain)
                    # Get Sitename domain and year (def year is 2025)
                    # And create a list of domain urns -> sitename
                    domain = conf.get(sitename, {}).get('domain', '')
                    year = conf.get(sitename, {}).get('year', 2025)
                    if domain and sitename:
                        domainUrns.setdefault(f"urn:ogf:network:{domain}:{year}", sitename)
        # Remove dir
        rmtree(repo, ignore_errors=True)
        # Save to cache file
        with open(fname, 'w', encoding="utf-8") as fd:
            fd.write(json.dumps({"fes": siteUrls, "domainUrns": domainUrns}))
        return siteUrls, domainUrns


# ---------------------------------------------------------
# RequestWrapper
# ---------------------------------------------------------

class RequestWrapper(GitRepo):
    """Request Wrapper for SENSE-SiteRM API"""

    def __init__(self):
        self.config = getConfig()
        # Remove self.cert after 1.6.X full migration on all Sites
        # self.cert is mainly needed for old releases (before 1.6.X), as all API calls require cert
        self.config['SITERM_CERT'] = self.config.get("SITERM_CERT", '/etc/grid-security/hostcert.pem')
        self.config['SITERM_KEY'] = self.config.get("SITERM_KEY", '/etc/grid-security/hostkey.pem')
        self.config['SITERM_VERIFY'] = False
        self.cert = (self.config['SITERM_CERT'], self.config['SITERM_KEY'])
        self._token_cache: Dict[str, dict] = {}
        self._site_caps: Dict[str, dict] = {}
        self._expiry_skew = int(self.config.get("SITERM_TOKEN_EXPIRY_SKEW", 60))

        super(RequestWrapper, self).__init__(self.config)

        self.fes, self.domainUrns = self.getAllSiteRMs()

        if not self.config.get("SITERM_VERIFY", False):
            urllib3.disable_warnings()

        self._loadTokenCache()


    def _loadTokenCache(self):
        """Load Token Cache"""
        if os.path.exists(AUTH_CACHE_FILE):
            try:
                with open(AUTH_CACHE_FILE, "r", encoding="utf-8") as f:
                    self._token_cache = json.load(f)
            except Exception:
                self._token_cache = {}

    def _saveTokenCache(self):
        """Save Token Cache"""
        os.makedirs(os.path.dirname(AUTH_CACHE_FILE), exist_ok=True)
        with open(AUTH_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(self._token_cache, f, indent=2)

    def _popToken(self, sitename):
        """Pop token out"""
        # Wipe out token in cache
        self._token_cache.pop(sitename, None)
        self._saveTokenCache()

    def _identifyauthmethod(self, config: dict):
        """Identify authentication method"""
        # Identify per site auth methods configured
        certauth = all(k in config for k in ["CERT", "KEY"])
        userpassauth = all(k in config for k in ["USERNAME", "PASSWORD"])
        accesstoken = "ACCESS_TOKEN" in config
        # Identify global auth methods configured
        gcertauth = all(k in self.config for k in ["SITERM_CERT", "SITERM_KEY"])
        guserpassauth = all(k in self.config for k in ["SITERM_USERNAME", "SITERM_PASSWORD"])
        gaccesstoken = "SITERM_ACCESS_TOKEN" in self.config

        return certauth or gcertauth, userpassauth or guserpassauth, accesstoken or gaccesstoken

    def _probeSiteCapabilities(self, sitename: str):
        """Check Site Capabilities for auth (also do alive, ready)"""
        if sitename in self._site_caps:
            return self._site_caps[sitename]

        base = self._getBaseUrl(sitename)
        caps = {"alive": False, "ready": False, "auth_methods": []}
        alive = requests.get(f"{base}/api/alive", cert=self.cert, timeout=getHTTPTimeout(), verify=False)
        if alive.ok:
            caps["alive"] = True if alive.json().get('status') == 'alive' else False
        else:
            raise Exception(f"Site {sitename} not alive. Response: {alive.text}")
        ready = requests.get(f"{base}/api/ready", cert=self.cert, timeout=getHTTPTimeout(), verify=False)
        if ready.ok:
            caps["ready"] = True if ready.json().get('status') == 'ready' else False
        else:
            raise Exception(f"Site {sitename} not ready. Response: {ready.text}")
        auth = requests.get(f"{base}/api/authentication-method",
                         cert=self.cert, timeout=getHTTPTimeout(), verify=False)
        if auth.ok:
            data = auth.json()
            if isinstance(data, dict):
                caps["auth_methods"] = [data]
            else:
                caps["auth_methods"] = data

        self._site_caps[sitename] = caps
        return caps


    def _resolveAuthConfig(self, sitename: str):
        """Resolve authentication configuration for a given site. Order:
            1) ACCESS_TOKEN
            2) X509
            3) USERPASS
            4) M2M"""
        caps = self._probeSiteCapabilities(sitename)
        supported = {c["auth_method"]: c for c in caps.get("auth_methods", [])}

        site_auth = self.config.get("SITERM_AUTH", {}).get(sitename, {})
        base = site_auth or {}

        certauth, userpassauth, accesstoken = self._identifyauthmethod(base)

        # 1. ACCESS_TOKEN
        if accesstoken and "ACCESS_TOKEN" in supported:
            return {"method": "token", "access_token": base["ACCESS_TOKEN"]}

        # 2. X509
        if certauth and "X509" in supported:
            return {"method": "cert",
                    "cert": base.get("CERT", self.config.get("SITERM_CERT")),
                    "key": base.get("KEY", self.config.get("SITERM_KEY"))}

        # 3. USERPASS
        if userpassauth and "USERPASS" in supported:
            cap = supported["USERPASS"]
            return {"method": "userpass",
                    "username": base.get("USERNAME", self.config.get("SITERM_USERNAME")),
                    "password": base.get("PASSWORD", self.config.get("SITERM_PASSWORD")),
                    "endpoint": cap.get("auth_endpoint")}

        # 4. M2M (last resort)
        if "M2M" in supported:
            cap = supported["M2M"]
            return {"method": "m2m", "endpoint": cap.get("auth_endpoint"),
                    "refresh_endpoint": cap.get("refresh_endpoint"),
                    "cert": base.get("CERT", self.config.get("SITERM_CERT")),
                    "key": base.get("KEY", self.config.get("SITERM_KEY"))}

        raise RuntimeError(f"No compatible authentication method for site {sitename}. Supported={list(supported.keys())}")

    def _token_valid(self, token: dict):
        """Check if the token is still valid"""
        return utcnow() < (token["expires_at"] - self._expiry_skew)

    def _getCachedToken(self, sitename: str):
        """Get cached token"""
        token = self._token_cache.get(sitename)
        if token:
            if self._token_valid(token):
                return token["access_token"]
            else:
                self._popToken(sitename)
        return None

    def _getRefreshToken(self, sitename: str):
        """Get refresh token"""
        refreshtoken = self._token_cache.get(sitename)
        if refreshtoken and refreshtoken.get("refresh_token"):
            return refreshtoken["refresh_token"]
        return None

    def _getSessionId(self, sitename: str):
        """Get session ID"""
        session = self._token_cache.get(sitename)
        if session and session.get("session_id"):
            return session["session_id"]
        return None

    def _storeToken(self, sitename: str, token_response: dict):
        """Store token in cache"""
        self._token_cache[sitename] = {
            "access_token": token_response["access_token"],
            "expires_at": token_response.get("expires_at", 0),
            "expires_in": token_response.get("expires_in", 0),
            "token_type": token_response.get("token_type", "Bearer"),
            "refresh_token": token_response.get("refresh_token"),
            "session_id": token_response.get("session_id")
        }
        self._saveTokenCache()

    def __getAccessTokenViaChallenge(self, sitename: str, authcfg: dict):
        """Get access token via challenge"""
        certPath = Path(authcfg.get("cert"))
        keyPath = Path(authcfg.get("key"))
        certText = certPath.read_text(encoding="utf-8")
        privateKeyBytes = keyPath.read_bytes()
        with httpx.Client(timeout=getHTTPTimeout()) as client:
            # --------------------------------------------------
            # 1. request challenge
            # --------------------------------------------------
            r = client.post(authcfg["endpoint"], json={"certificate": certText})
            r.raise_for_status()
            challenge_resp = r.json()
            # --------------------------------------------------
            # 2. sign challenge
            # --------------------------------------------------
            signature = sign_challenge(challenge_resp["challenge"], privateKeyBytes)
            # --------------------------------------------------
            # 3. exchange signature for tokens
            # --------------------------------------------------
            tokenresp = client.post(challenge_resp["ref_url"], json={"signature": signature})
            tokenresp.raise_for_status()
            out = tokenresp.json()
        return out


    def __getAccessTokenViaUserPass(self, sitename: str, authcfg: dict):
        """Get access token via username and password"""
        with httpx.Client(timeout=getHTTPTimeout()) as client:
            try:
                resp = client.post(authcfg["endpoint"], json={"username": authcfg["username"], "password": authcfg["password"]})
                resp.raise_for_status()
                out = resp.json()
            except httpx.HTTPStatusError as ex:
                if ex.response.status_code in [400, 401]:
                    self._popToken(sitename)
                    return {}
                else:
                    raise
        return out

    def __getAccessTokenViaRefresh(self, sitename: str, authcfg: dict):
        refresh_token = self._getRefreshToken(sitename)
        session_id = self._getSessionId(sitename)
        if not refresh_token or not session_id:
            return {}
        with httpx.Client(timeout=getHTTPTimeout()) as client:
            try:
                resp = client.post(authcfg["refresh_endpoint"],
                                   json={"session_id": session_id,
                                         "refresh_token": refresh_token})
                resp.raise_for_status()
                refreshed = resp.json()
            except httpx.HTTPStatusError as ex:
                if ex.response.status_code in [400, 401]:
                    self._popToken(sitename)
                    return {}
                else:
                    raise
        return refreshed


    def _getAccessToken(self, sitename: str, authcfg: dict):
        """Get access token for a given site"""
        cached = self._getCachedToken(sitename)
        if cached:
            return cached
        refreshtoken = self.__getAccessTokenViaRefresh(sitename, authcfg)
        if refreshtoken:
            print(refreshtoken)
            self._storeToken(sitename, refreshtoken)
            return refreshtoken["access_token"]
        if authcfg["method"] == "m2m":
            token = self.__getAccessTokenViaChallenge(sitename, authcfg)
            self._storeToken(sitename, token)
            return token["access_token"]
        if authcfg["method"] == "userpass":
            token = self.__getAccessTokenViaUserPass(sitename, authcfg)
            self._storeToken(sitename, token)
            return token["access_token"]
        # All options been tried out. Fail
        raise Exception("Failed to get access token")

    def _getBaseUrl(self, sitename):
        """Get Full URL"""
        if sitename not in self.fes.keys():
            raise Exception(f"Sitename {sitename} not found in SiteRM configs")
        return self.fes[sitename].rstrip('/')

    def makeRequest(self, sitename: str, url: str, **kwargs):
        """Make HTTP Request"""
        verb = kwargs.get("verb")
        if verb not in {"GET", "POST", "PUT"}:
            raise Exception("Invalid verb")

        authcfg = self._resolveAuthConfig(sitename)

        headers = {}
        req_kwargs = {"json": kwargs.get("data"), "params": kwargs.get("urlparams")}

        cert = None

        if authcfg["method"] == "token":
            headers["Authorization"] = f"Bearer {authcfg['access_token']}"

        elif authcfg["method"] in {"m2m", "userpass"}:
            headers["Authorization"] = f"Bearer {self._getAccessToken(sitename, authcfg)}"

        elif authcfg["method"] == "cert":
            cert = (authcfg["cert"], authcfg["key"])

        req_kwargs["headers"] = headers

        base = self._getBaseUrl(sitename)
        full_url = f"{base}/{url.lstrip('/')}"

        with httpx.Client(timeout=getHTTPTimeout(), verify=self.config["SITERM_VERIFY"], cert=cert) as client:
            resp = client.request(verb, full_url, **req_kwargs)
        try:
            return resp.json(), resp.is_success, resp
        except Exception:
            return resp.text, resp.is_success, resp
