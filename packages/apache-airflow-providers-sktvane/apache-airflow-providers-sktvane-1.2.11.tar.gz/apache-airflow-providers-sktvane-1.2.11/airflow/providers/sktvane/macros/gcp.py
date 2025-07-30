import json

from google.cloud import bigquery, storage
from google.oauth2 import service_account

from ..macros.vault import get_secrets


def _get_credentials():
    key = get_secrets("gcp/skt-datahub/dataflow")["config"]
    json_acct_info = json.loads(key)
    credentials = service_account.Credentials.from_service_account_info(json_acct_info)
    scoped_credentials = credentials.with_scopes(
        ["https://www.googleapis.com/auth/cloud-platform"]
    )

    return scoped_credentials


def bigquery_client():
    return bigquery.Client(
        credentials=_get_credentials(),
        project="skt-datahub",
        location="asia-northeast3",
    )


def gcs_client():
    return storage.Client(
        credentials=_get_credentials(),
        project="skt-datahub",
    )
