import hvac

vault_client = hvac.Client()


def get_secrets(path, parse_data=True):
    data = vault_client.secrets.kv.v2.read_secret_version(path=path)
    if parse_data:
        data = data["data"]["data"]
    return data
