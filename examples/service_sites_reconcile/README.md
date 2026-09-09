# Service Sites Reconcile

This script assembles the `setinstancestartend` curl commands needed to reconcile a SENSE
service instance with the Site RMs that carry it. Given a service instance UUID it queries
the system-wide model through the WorkflowCombinedApi for the instance's l2-services
(`mrs:SwitchingSubnet`) and l3-services (`mrs:RoutingTable`), resolves each service URI to
its domain root URI with the DiscoverApi, reads the `sitename` and `metadata:webdomain`
published by that domain's metadata service, and prints one curl command per service.

```
python cleanup_service_all_sites.py <instance-uuid> [--start ...] [--end ...] [--duration ...]
```

The start and end of the window accept either epoch seconds or an offset from now, using the
suffixes `s`, `m`, `h`, `d` — `+10m` for ten minutes ahead, `-10d` for ten days back. When
`--end` is omitted the window runs for `--duration` (default `1d`) from the start.

```
--start +10m --end +10h      # a window opening ten minutes from now
--start -10d --end -9d       # a one-day window last week
--start 1767287460           # absolute epoch seconds, plus the default 1d duration
```

By default the Authorization header carries the literal `<TOKEN>` placeholder. Three options
fill it in instead:

| option | token |
| --- | --- |
| `--fetch-token [--cert PATH --key PATH]` | one per site, minted by M2M x509 challenge/response against that site's SiteRM |
| `--sense-token` | one SENSE-O token, from the SENSE auth config, reused for every site |
| `--with-token TOKEN` | the token you pass, reused for every site |

`--fetch-token` is the one that matches how these endpoints authenticate: the generated
commands target each Site RM's own API root rather than SENSE-O, so a SENSE-O token is not
necessarily the credential they accept. It goes through the SiteRM client in
`sense/client/siterm`, which posts the certificate to the site's M2M auth endpoint, signs the
returned challenge with the private key (RSA-PSS or ECDSA, SHA256), and posts the signature
back for the token. Capabilities and tokens are cached per site — in `~/.siterm/auth.json`
and reused until they expire — so a site carrying several services of the instance is only
exchanged with once. The token is minted against the same apiroot the curl command targets.
`--cert`/`--key` default to `SITERM_CERT`/`SITERM_KEY` from the SENSE auth config, falling
back to `/etc/grid-security/hostcert.pem` and `hostkey.pem`. A site that offers no M2M auth
method is reported on stderr and skipped, as is any site whose exchange fails.

Nothing is sent by default — the script only prints the commands, so you can review them and
pipe them to a shell yourself. Pass `--commit` to send the requests directly instead, which
needs a real token and so is refused alongside the `<TOKEN>` placeholder:

```
python cleanup_service_all_sites.py <instance-uuid> --start +10m --duration 1d --fetch-token --commit
```

Each request then reports its HTTP status and response body, and the script exits non-zero if
any of them failed:

```
# l2 service at T1_US_FNAL (urn:ogf:network:fnal.gov:2023)
POST https://cmssense1.fnal.gov:8443/api/T1_US_FNAL/setinstancestartend -> 200
  {"status":"OK"}

# l3 service at T1_US_FNAL (urn:ogf:network:fnal.gov:2023)
POST https://cmssense1.fnal.gov:8443/api/T1_US_FNAL/setinstancestartend -> 401
  {"error":"token expired"}
```

A request that never got a response — a refused connection, a timeout — reports `FAILED` with
the error in place of a status code. With `--json`, each record gains `status_code` and
`response` fields instead. Requests go out through `requests`, built from the same url,
headers and body as the printed curl command, so what runs is what was shown.

Without `--commit`, each service produces a commented header line followed by its curl command:

```
# l3 service at T2_US_SDSC (urn:ogf:network:nrp-nautilus.io:2020)
curl 'https://sense-prpdev.nrp-nautilus.io/api/T2_US_SDSC/setinstancestartend' \
  -X POST \
  -H 'Authorization: Bearer <TOKEN>' \
  -H 'Content-Type: application/json' \
  --data-raw '{"sitename":"T2_US_SDSC","instanceid":"urn:ogf:network:nrp-nautilus.io:2020:sn3700_s0:service+rst-ipv6:table+3bae89fc","starttimestamp":1767287460,"endtimestamp":1767373860}'
```

Pass `--json` to emit the resolved records (type, uri, root_uri, sitename, apiroot, curl) as
JSON instead. A single instance typically spans several sites, and a site that carries both
an l2 and an l3 service of the instance is resolved once and appears under the same
`root_uri` twice:

```json
[
  {
    "type": "l2",
    "uri": "urn:ogf:network:t2-us-ucsd.edu:2025:edgecore_s0:service+vsw:conn+e5478dc9-088b-4e0d-9ea3-d12baef3206b:vt+l2-policy-Connection_1:vlan+3131",
    "root_uri": "urn:ogf:network:t2-us-ucsd.edu:2025",
    "sitename": "T2_US_UCSD",
    "apiroot": "https://sense-t2-us-ucsd.nrp-nautilus.io:443",
    "curl": "curl 'https://sense-t2-us-ucsd.nrp-nautilus.io:443/api/T2_US_UCSD/setinstancestartend' \\\n  -X POST \\\n  -H 'Authorization: Bearer <TOKEN>' \\\n  -H 'Content-Type: application/json' \\\n  --data-raw '{\"sitename\":\"T2_US_UCSD\",\"instanceid\":\"urn:ogf:network:t2-us-ucsd.edu:2025:edgecore_s0:service+vsw:conn+e5478dc9-088b-4e0d-9ea3-d12baef3206b:vt+l2-policy-Connection_1:vlan+3131\",\"starttimestamp\":1788965593,\"endtimestamp\":1789051993}'"
  },
  {
    "type": "l2",
    "uri": "urn:ogf:network:sense-oasis-nrp-nautilus.io:2020:oasis:service+vsw:conn+e5478dc9-088b-4e0d-9ea3-d12baef3206b:vt+l2-policy-Connection_1:vlan+3131",
    "root_uri": "urn:ogf:network:sense-oasis-nrp-nautilus.io:2020",
    "sitename": "T2_US_UCSD_OASIS",
    "apiroot": "https://sense-oasis.nrp-nautilus.io:443",
    "curl": "curl 'https://sense-oasis.nrp-nautilus.io:443/api/T2_US_UCSD_OASIS/setinstancestartend' \\\n  -X POST \\\n  -H 'Authorization: Bearer <TOKEN>' \\\n  -H 'Content-Type: application/json' \\\n  --data-raw '{\"sitename\":\"T2_US_UCSD_OASIS\",\"instanceid\":\"urn:ogf:network:sense-oasis-nrp-nautilus.io:2020:oasis:service+vsw:conn+e5478dc9-088b-4e0d-9ea3-d12baef3206b:vt+l2-policy-Connection_1:vlan+3131\",\"starttimestamp\":1788965593,\"endtimestamp\":1789051993}'"
  },
  {
    "type": "l2",
    "uri": "urn:ogf:network:fnal.gov:2023:cisconx9:service+vsw:conn+e5478dc9-088b-4e0d-9ea3-d12baef3206b:vt+l2-policy-Connection_1:vlan+3613",
    "root_uri": "urn:ogf:network:fnal.gov:2023",
    "sitename": "T1_US_FNAL",
    "apiroot": "https://cmssense1.fnal.gov:8443",
    "curl": "curl 'https://cmssense1.fnal.gov:8443/api/T1_US_FNAL/setinstancestartend' \\\n  -X POST \\\n  -H 'Authorization: Bearer <TOKEN>' \\\n  -H 'Content-Type: application/json' \\\n  --data-raw '{\"sitename\":\"T1_US_FNAL\",\"instanceid\":\"urn:ogf:network:fnal.gov:2023:cisconx9:service+vsw:conn+e5478dc9-088b-4e0d-9ea3-d12baef3206b:vt+l2-policy-Connection_1:vlan+3613\",\"starttimestamp\":1788965593,\"endtimestamp\":1789051993}'"
  },
  {
    "type": "l3",
    "uri": "urn:ogf:network:fnal.gov:2023:cisconx9:service+rst-ipv6:table+e5478dc9-088b-4e0d-9ea3-d12baef3206b",
    "root_uri": "urn:ogf:network:fnal.gov:2023",
    "sitename": "T1_US_FNAL",
    "apiroot": "https://cmssense1.fnal.gov:8443",
    "curl": "curl 'https://cmssense1.fnal.gov:8443/api/T1_US_FNAL/setinstancestartend' \\\n  -X POST \\\n  -H 'Authorization: Bearer <TOKEN>' \\\n  -H 'Content-Type: application/json' \\\n  --data-raw '{\"sitename\":\"T1_US_FNAL\",\"instanceid\":\"urn:ogf:network:fnal.gov:2023:cisconx9:service+rst-ipv6:table+e5478dc9-088b-4e0d-9ea3-d12baef3206b\",\"starttimestamp\":1788965593,\"endtimestamp\":1789051993}'"
  },
  {
    "type": "l3",
    "uri": "urn:ogf:network:t2-us-ucsd.edu:2025:edgecore_s0:service+rst-ipv6:table+e5478dc9-088b-4e0d-9ea3-d12baef3206b",
    "root_uri": "urn:ogf:network:t2-us-ucsd.edu:2025",
    "sitename": "T2_US_UCSD",
    "apiroot": "https://sense-t2-us-ucsd.nrp-nautilus.io:443",
    "curl": "curl 'https://sense-t2-us-ucsd.nrp-nautilus.io:443/api/T2_US_UCSD/setinstancestartend' \\\n  -X POST \\\n  -H 'Authorization: Bearer <TOKEN>' \\\n  -H 'Content-Type: application/json' \\\n  --data-raw '{\"sitename\":\"T2_US_UCSD\",\"instanceid\":\"urn:ogf:network:t2-us-ucsd.edu:2025:edgecore_s0:service+rst-ipv6:table+e5478dc9-088b-4e0d-9ea3-d12baef3206b\",\"starttimestamp\":1788965593,\"endtimestamp\":1789051993}'"
  }
]
```

An instance may hold l2-services, l3-services, both, or neither; a missing kind is simply
absent from the output. Domains that publish no Site RM metadata service are reported once
each on stderr as `skip non-SiteRM domain <root_uri>` and contribute no curl command. Any
other per-service failure is reported on stderr and skipped so it cannot hide the rest.
