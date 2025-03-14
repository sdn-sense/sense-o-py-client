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
