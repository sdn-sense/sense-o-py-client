#!/usr/bin/env python3
# pylint: disable=line-too-long
# -*- coding: utf-8 -*-
"""
Assemble `setinstancestartend` curl commands for the L2/L3 services of a SENSE instance.

For a given service instance UUID this script:
  1. queries the system-wide model for the l2-services (mrs:SwitchingSubnet) and
     l3-services (mrs:RoutingTable) whose URI contains that UUID,
  2. resolves each service URI to its domain root URI,
  3. reads the sitename and the metadata:webdomain (apiroot) published by that
     domain's metadata service,
  4. prints one curl command per service.

Templates are posted with si_uuid unset, so the client wraps them in an XML
<jsonTemplate> envelope (see workflow_combined_api.instance_si_uuid_manifest_post_with_http_info).
Angle brackets inside a SPARQL query must therefore be XML-escaped as &lt; / &gt;.
"""
import argparse
import json
import re
import sys
import time

from sense.client.apiclient import ApiClient
from sense.client.discover_api import DiscoverApi
from sense.client.workflow_combined_api import WorkflowCombinedApi

# Placeholders come back verbatim (e.g. "?subnet?") when a non-required block matches nothing.
PLACEHOLDER_RE = re.compile(r"^\?.*\?$")

SERVICES_TEMPLATE = {
    "l2-services": [
        {
            "uri": "?subnet?",
            "sparql-ext": "SELECT ?subnet WHERE { ?subnet a mrs:SwitchingSubnet.  FILTER(CONTAINS(STR(?subnet), '{uuid}')) }",
            "required": "false",
        }
    ],
    "l3-services": [
        {
            "uri": "?rtable?",
            "sparql-ext": "SELECT ?rtable WHERE { ?rtable a mrs:RoutingTable.  FILTER(CONTAINS(STR(?rtable), '{uuid}')) }",
            "required": "false",
        }
    ],
}

SITE_RM_TEMPLATE = {
    "Site RM": {
        "sitename": "?sitename?",
        "apiroot": "?webdomain?",
        "sparql-ext": "SELECT DISTINCT ?sitename ?webdomain WHERE { &lt;{root_uri}&gt; nml:hasService ?md_svc .  ?md_svc mrs:hasNetworkAttribute ?sn .  ?sn mrs:tag '/sitename' .  ?sn mrs:value ?sitename .  ?md_svc mrs:hasNetworkAddress ?wd .  ?wd mrs:type 'metadata:webdomain' .  ?wd mrs:value ?webdomain .  }",
        "required": "true",
    }
}


DURATION_RE = re.compile(r"^([+-]?\d+)([smhd]?)$")
UNIT_SECONDS = {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400}


def parse_duration(value):
    """Parse a duration such as 10s, 10m, 10h, 10d (bare number = seconds) into seconds."""
    match = DURATION_RE.match(str(value).strip())
    if not match:
        raise argparse.ArgumentTypeError(f"invalid duration {value!r}: expected e.g. 3600, 10s, 10m, 10h or 10d")
    return int(match.group(1)) * UNIT_SECONDS[match.group(2)]


TIME_OPTIONS = ("--start", "--end", "--duration")


def join_negative_offsets(argv):
    """Fold "--start -10h" into "--start=-10h".

    Before Python 3.14 argparse reads a value like -10h as an option name and bails out
    with "expected one argument", so past offsets have to be attached with '='.
    """
    joined, skip = [], False
    for index, arg in enumerate(argv):
        if skip:
            skip = False
            continue
        following = argv[index + 1] if index + 1 < len(argv) else ""
        if arg in TIME_OPTIONS and following.startswith("-") and DURATION_RE.match(following):
            joined.append(f"{arg}={following}")
            skip = True
        else:
            joined.append(arg)
    return joined


def parse_timespec(value, now):
    """Parse an absolute epoch timestamp, or a signed offset from now such as +10s/+10h/-10d."""
    text = str(value).strip()
    if text.startswith(("+", "-")) or text[-1:] in ("s", "m", "h", "d"):
        return now + parse_duration(text)
    if not text.isdigit():
        raise argparse.ArgumentTypeError(
            f"invalid timestamp {value!r}: expected epoch seconds, or an offset from now like +10s, +10m, +10h, +10d"
        )
    return int(text)


class NonSiteRMDomain(Exception):
    """Raised when a domain publishes no Site RM metadata service (sitename + webdomain)."""


def is_resolved(value):
    """True when a manifest field holds a real value rather than an unfilled placeholder."""
    return bool(value) and not PLACEHOLDER_RE.match(str(value).strip())


def render(template, **subs):
    """Substitute {name} fields in a template's string leaves."""
    rendered = json.dumps(template)
    for key, val in subs.items():
        rendered = rendered.replace("{" + key + "}", val)
    return rendered


def run_manifest(workflow_api, body):
    """POST a manifest template against the system-wide model and return its jsonTemplate."""
    response = workflow_api.manifest_create(body)
    if not response or "jsonTemplate" not in response:
        raise ValueError(f"Invalid response from SENSE manifest creation: {response}")
    return json.loads(response["jsonTemplate"])


def get_services(workflow_api, uuid):
    """Return [(kind, uri)] for the l2 and l3 services matching uuid; may be empty."""
    manifest = run_manifest(workflow_api, render(SERVICES_TEMPLATE, uuid=uuid))
    services = []
    for kind, key in (("l2", "l2-services"), ("l3", "l3-services")):
        for entry in manifest.get(key) or []:
            uri = entry.get("uri")
            if is_resolved(uri):
                services.append((kind, uri.strip()))
    return services


def get_root_uri(discover_api, uri):
    """Resolve a resource URI to its domain root URI."""
    root_uri = discover_api.discover_lookup_rooturi_get(uri)
    if not root_uri or "ERROR" in str(root_uri):
        raise ValueError(f"Root URI lookup failed for {uri}: {root_uri}")
    return str(root_uri).strip().strip('"')


def get_site_rm(workflow_api, root_uri):
    """Return (sitename, apiroot) published by the metadata service of root_uri."""
    try:
        manifest = run_manifest(workflow_api, render(SITE_RM_TEMPLATE, root_uri=root_uri))
    except ValueError as exc:
        # SENSE-O answers a manifest query that matches nothing with a 500 whose body reads
        # "no required re[q]sult for manifest query for: ..." - that just means this domain
        # has no Site RM metadata service, not that the query itself is broken.
        message = str(getattr(exc, "json", {}).get("message", ""))
        if "no required" in message and "manifest query" in message:
            raise NonSiteRMDomain(root_uri) from exc
        raise
    site_rm = manifest.get("Site RM") or {}
    if isinstance(site_rm, list):
        site_rm = site_rm[0] if site_rm else {}
    sitename, apiroot = site_rm.get("sitename"), site_rm.get("apiroot")
    if not is_resolved(sitename) or not is_resolved(apiroot):
        raise NonSiteRMDomain(root_uri)
    return sitename.strip(), apiroot.strip().rstrip("/")


def make_siterm_m2m_resolver(cert, key):
    """Return sitename -> bearer token, minted per site by M2M x509 challenge/response.

    The exchange itself lives in the SiteRM client: POST the certificate to the site's
    M2M auth endpoint, sign the returned challenge with the private key, post the
    signature back for the token. Tokens are cached by that client in ~/.siterm/auth.json
    and reused until they expire.
    """
    # Imported lazily: the SiteRM client pulls in httpx, GitPython and cryptography, and
    # constructing it clones the rm-configs repo, which is wasted work for the other modes.
    from sense.client.siterm.requestwrapper import RequestWrapper as SiteRMRequestWrapper

    wrapper = SiteRMRequestWrapper()
    if cert:
        wrapper.config["SITERM_CERT"] = cert
    if key:
        wrapper.config["SITERM_KEY"] = key
    wrapper.cert = (wrapper.config["SITERM_CERT"], wrapper.config["SITERM_KEY"])

    def resolve(sitename, apiroot):
        # Mint the token against the same host the curl command targets, rather than
        # whatever webdomain rm-configs carries for this site.
        wrapper.fes[sitename] = apiroot
        supported = {c["auth_method"]: c for c in wrapper._probeSiteCapabilities(sitename).get("auth_methods", [])}
        if "M2M" not in supported:
            raise ValueError(f"site {sitename} does not offer M2M auth (offers {sorted(supported) or 'nothing'})")
        capability = supported["M2M"]
        return wrapper._getAccessToken(
            sitename,
            {
                "method": "m2m",
                "endpoint": capability.get("auth_endpoint"),
                "refresh_endpoint": capability.get("refresh_endpoint"),
                "cert": wrapper.config["SITERM_CERT"],
                "key": wrapper.config["SITERM_KEY"],
            },
        )

    return resolve


def make_token_resolver(args):
    """Return sitename, apiroot -> bearer token for the selected token mode."""
    if args.fetch_token:
        return make_siterm_m2m_resolver(args.cert, args.key)
    if args.sense_token:
        token = ApiClient(None).token["access_token"]
    elif args.with_token:
        token = args.with_token
    else:
        token = "<TOKEN>"
    return lambda sitename, apiroot: token


def shell_quote(value):
    """Wrap value in single quotes the way the reference curl command does."""
    return "'" + str(value).replace("'", "'\\''") + "'"


def build_curl(sitename, apiroot, instance_id, start, end, token):
    """Assemble the setinstancestartend curl command for one service."""
    payload = json.dumps(
        {
            "sitename": sitename,
            "instanceid": instance_id,
            "starttimestamp": start,
            "endtimestamp": end,
        },
        separators=(",", ":"),
    )
    return "\n".join(
        [
            f"curl {shell_quote(f'{apiroot}/api/{sitename}/setinstancestartend')} \\",
            "  -X POST \\",
            f"  -H {shell_quote(f'Authorization: Bearer {token}')} \\",
            f"  --data-raw {shell_quote(payload)}",
        ]
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("uuid", help="service instance UUID to match in the l2/l3 service URIs")
    parser.add_argument("--start", help="start time: epoch seconds, or an offset from now such as +10s, +10m, +10h, +10d, or -10h/-10d for the past (default: now)")
    parser.add_argument("--end", help="end time: epoch seconds, or an offset from now such as +10h or -10m (default: start + --duration)")
    parser.add_argument("--duration", type=parse_duration, default="1d", help="length of the window from start when --end is omitted, e.g. 3600, 10s, 10m, 10h, 10d (default: 1d)")
    token_group = parser.add_mutually_exclusive_group()
    token_group.add_argument("--fetch-token", action="store_true", help="mint a per-site bearer token by M2M x509 challenge/response against each site's SiteRM")
    token_group.add_argument("--sense-token", action="store_true", help="fetch one bearer token from the SENSE auth config (SENSE_AUTH_OVERRIDE, /etc/sense-o-auth.yaml or ~/.sense-o-auth.yaml) and inline it for every site")
    token_group.add_argument("--with-token", metavar="TOKEN", help="inline this bearer token instead of the <TOKEN> placeholder")
    parser.add_argument("--cert", help="x509 certificate for --fetch-token (default: SITERM_CERT from the SENSE auth config, else /etc/grid-security/hostcert.pem)")
    parser.add_argument("--key", help="x509 private key for --fetch-token (default: SITERM_KEY from the SENSE auth config, else /etc/grid-security/hostkey.pem)")
    parser.add_argument("--json", action="store_true", help="emit the resolved records as JSON instead of curl commands")
    args = parser.parse_args(join_negative_offsets(sys.argv[1:]))

    now = int(time.time())
    try:
        start = parse_timespec(args.start, now) if args.start is not None else now
        end = parse_timespec(args.end, now) if args.end is not None else start + args.duration
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    if end <= start:
        parser.error(f"end timestamp {end} is not after start timestamp {start}")

    if (args.cert or args.key) and not args.fetch_token:
        parser.error("--cert/--key only apply to --fetch-token")
    token_for = make_token_resolver(args)

    workflow_api = WorkflowCombinedApi()
    discover_api = DiscoverApi()

    services = get_services(workflow_api, args.uuid)
    if not services:
        print(f"No l2-services or l3-services found for {args.uuid}", file=sys.stderr)
        return 0

    site_cache = {}  # root_uri -> (sitename, apiroot), or None for a non-SiteRM domain
    records, failures = [], 0
    for kind, uri in services:
        try:
            root_uri = get_root_uri(discover_api, uri)
            if root_uri not in site_cache:
                try:
                    site_cache[root_uri] = get_site_rm(workflow_api, root_uri)
                except NonSiteRMDomain:
                    site_cache[root_uri] = None
                    print(f"skip non-SiteRM domain {root_uri}", file=sys.stderr)
            if site_cache[root_uri] is None:  # already reported for this domain
                continue
            sitename, apiroot = site_cache[root_uri]
            token = token_for(sitename, apiroot)
        except Exception as exc:  # keep going so one bad service does not hide the rest
            print(f"Skipping {kind} service {uri}: {exc}", file=sys.stderr)
            failures += 1
            continue
        records.append(
            {
                "type": kind,
                "uri": uri,
                "root_uri": root_uri,
                "sitename": sitename,
                "apiroot": apiroot,
                "curl": build_curl(sitename, apiroot, uri, start, end, token),
            }
        )

    if args.json:
        print(json.dumps(records, indent=2))
    else:
        for record in records:
            print(f"# {record['type']} service at {record['sitename']} ({record['root_uri']})")
            print(record["curl"])
            print()

    return 1 if failures and not records else 0


if __name__ == "__main__":
    sys.exit(main())
