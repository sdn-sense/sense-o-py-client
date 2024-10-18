import enum

AUTH_ENDPOINT = "auth_endpoint"
API_ENDPOINT = "api_endpoint"
CLIENT_ID = "client_id"
USERNAME = "username"
PASSWORD = "password"
SECRET = "secret"

SENSE_CONF_ATTRS = [AUTH_ENDPOINT, API_ENDPOINT, CLIENT_ID, USERNAME, PASSWORD, SECRET]

SENSE_PROFILE_UID = "service_profile_uuid"
SENSE_ALIAS = "alias"
SENSE_EDIT = "options"
SENSE_URI = 'uri'
# SENSE_ID = 'id'
SENSE_PATH = 'path'
SENSE_VLAN_TAG = 'vlan_tag'


SERVICE_INSTANCE_KEYS = ['intents', 'referenceUUID', 'state']

SENSE_CUSTOMER_ASN = "customer_asn"
SENSE_AMAZON_ASN = "amazon_asn"
SENSE_GOOGLE_ASN = "google_asn"
SENSE_CUSTOMER_IP = "customer_ip"
SENSE_AMAZON_IP = "amazon_ip"
SENSE_GOOGLE_IP = "google_ip"
SENSE_AUTHKEY = "authkey"
SENSE_TO_HOSTED_CONN = "to_hosted_conn"

SENSE_GCP_PEERING_MAPPING = {
    'local_asn': SENSE_CUSTOMER_ASN,
    'local_address': SENSE_CUSTOMER_IP,
    'remote_asn': SENSE_GOOGLE_ASN,
    'remote_address': SENSE_GOOGLE_IP,
    'RES_SECURITY': SENSE_AUTHKEY
}

SENSE_KEYPAIR = 'Key Pair'
SENSE_PUBLIC_IP = 'Public IP'
SENSE_PRIVATE_IP = 'Private IP'
SENSE_NODE_NAME = 'Node Name'
SENSE_IMAGE = 'Image'

SENSE_RETRY = 50


class SupportedCloud(str, enum.Enum):
    """
    The Cloud supported by SENSE.
    """
    GCP = "GOOGLE"
