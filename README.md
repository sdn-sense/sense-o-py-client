## SENSE Orchestrator Python Client

### Example ~/.sense-o-auth.yaml (or /etc/sense-o-auth.yaml)
```
AUTH_ENDPOINT: https://dev1.virnao.com:8543/auth/realms/StackV/protocol/openid-connect/token
# dev1
API_ENDPOINT: https://dev1.virnao.com:8443/StackV-web/restapi
# localhost
#API_ENDPOINT: https://localhost:8443/StackV-web/restapi
CLIENT_ID: StackV
USERNAME: some username
PASSWORD: some passpass
SECRET: some api key
verify: True 
# verify: False --  for servers without verifiabe SSL cert
```
