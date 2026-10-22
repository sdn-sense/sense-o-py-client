## SENSE Orchestrator Python Client

### Template for ~/.sense-o-auth.yaml (or /etc/sense-o-auth.yaml)

```
AUTH_ENDPOINT: https://sense-o.es.net:8543/auth/realms/StackV/protocol/openid-connect/token
API_ENDPOINT: https://sense-o.es.net:8443/StackV-web/restapi
# API_ENDPOINT: https://localhost:8443/StackV-web/restapi -- for local test env
CLIENT_ID: StackV
USERNAME: some username
PASSWORD: some passpass
SECRET: some api key
verify: True 
# verify: False --  for servers without verifiabe SSL cert
```

### Profile Submission Guidance

You may query a profile before creating an instance to see which license principals you
can use and which projects belong to each choice:

```sh
sense_util.py --profile-options -u PROFILE_UUID --json # get all options for a profile by UUID.
sense_util.py --profile-options -n "Science Profile" # get all options for a profile by name.
sense_util.py --profile-options -u PROFILE_UUID --principal /science/team --json # get options for a profile for a single licensed principal.
```

The response includes profile metadata and a list of their licensed `principals`. Each entry reports:

- `principal`: the principal that can be passed with `--principal`.
- `source`: Whether it's a `license` or the personal submission path for an `owner` or `admin`.
- `allocations`, `used`, and `remaining`: basic information about the license capacity.
- `selectable`: whether capacity permits this choice. Exhausted licenses remain
  visible with `selectable: false`. Profile owners/admins naturally bypass limits.
- `readOnly`: whether the license restricts profile editing.
- `projects`: projects offered for that principal, to be passed with `--project`.
- `suggestedProject`: the first offered project, as suggested by the portal.
- `projectRequired`: compat for portal selection rule requiring an explicit project choice.

To inspect your own memberships or projects independently:

```sh
sense_util.py --groups --json
sense_util.py --projects --json
sense_util.py --projects --principal /science/team --json
```

`--groups` reads your memberships from the current API access token and includes inherited parent groups.
Group membership alone does not establish a usable license for a given profile.

### Instance Principal and Project Selection

`--create` and `--compute` accept these options:

- `--principal`: the user, email, or group path to submit under (from `--profile-options`).
- `--group`: alias for `--principal`; pick one or the other.
- `--project`: the project's external ID or name to attribute the instance to.
- `--use-defaults`: acknowledge an omitted principal or project and silence their warnings.

```sh
sense_util.py --create -f intent.json --group /science/team --project PRJ-42
sense_util.py --compute -u PROFILE_UUID --principal alice@example.org --use-defaults
```

These flags simply override the intent's `principal` and `project` fields. If either is omitted, the
server defaults apply and the CLI prints a warning on stderr.
