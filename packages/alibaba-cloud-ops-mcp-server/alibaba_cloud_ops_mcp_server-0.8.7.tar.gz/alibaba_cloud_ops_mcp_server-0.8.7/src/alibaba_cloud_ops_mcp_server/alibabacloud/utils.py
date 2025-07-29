from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_tea_openapi.models import Config


def create_config():
    credentialsClient = CredClient()
    config = Config(credential=credentialsClient)
    config.user_agent = 'alibaba-cloud-ops-mcp-server'
    return config
