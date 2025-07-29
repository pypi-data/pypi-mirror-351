import logging
from typing import List, Tuple, Optional
from dataclasses import dataclass

import pandas as pd
from dotenv import load_dotenv
import os
from google.cloud import secretmanager
from elasticsearch import Elasticsearch


# Define a class for the connection configuration
@dataclass(frozen=True)
class ConnectionConfiguration:
    """A simple data class that holds the connection parameters to Elasticsearch.
    Args:
         hosts: A list of URLs of the Elasticsearch nodes to connect to.
         http_auth: A tuple of username and password for HTTP authentication.
         cloud_id: A connection string that configures your client to work with your Elastic Cloud deployment
         verify_certs: A boolean indicating whether to verify SSL certificates.
         ca_certs: A path to a CA certificate file or a directory with certificates.
         client_cert: A path to a client certificate file.
         client_key: A path to a client key file.
         ssl_version: The SSL version to use.
         ssl_assert_hostname: A boolean indicating whether to verify the hostname in the certificate.
         ssl_assert_fingerprint: A hex string of the expected certificate fingerprint.
    """

    hosts: Optional[List[str]] = None
    http_auth: Optional[Tuple[str, str]] = None
    cloud_id: Optional[str] = None
    verify_certs: Optional[bool] = False
    ca_certs: Optional[str] = None
    client_cert: Optional[str] = None
    client_key: Optional[str] = None
    ssl_version: Optional[int] = None
    ssl_assert_hostname: Optional[bool] = None
    ssl_assert_fingerprint: Optional[str] = None

load_dotenv()

def get_elastic_cloud_location() -> str:
    elastic_cloud_location = os.environ.get("ELASTIC_CLOUD_ID_LOCATION") or os.getenv("ELASTIC_CLOUD_ID_LOCATION")
    if not elastic_cloud_location:
        raise ValueError("ELASTIC_CLOUD_ID_LOCATION must be set in environment variables.")
    return elastic_cloud_location

def get_elastic_auth() -> str:
    elastic_auth = os.environ.get("ELASTIC_HTTP_AUTH") or os.getenv("ELASTIC_HTTP_AUTH")
    if not elastic_auth:
        raise ValueError("ELASTIC_HTTP_AUTH must be set in environment variables.")
    return elastic_auth

def get_elastic_cloud_id() -> str:
    elastic_cloud_id = os.environ.get("ELASTIC_CLOUD_ID") or os.getenv("ELASTIC_CLOUD_ID")
    if not elastic_cloud_id:
        raise ValueError("ELASTIC_CLOUD_ID must be set in environment variables.")
    return elastic_cloud_id


class ElasticSearch:
    """A simple data class that holds the connection parameters to Elasticsearch."""

    def __init__(self, elastic_cloud_id=None) -> None:
        env = os.environ.get("ENV", "CLOUD")
        logging.info(f"ElasticSearch environment variable: {env}")
        if env == "LOCAL":
            self.elastic_cloud_id = get_elastic_cloud_id()
            self.elastic_auth = get_elastic_auth()
        else:
            secret_manager_client = secretmanager.SecretManagerServiceClient()
            secret_response = secret_manager_client.access_secret_version(
                request={"name": get_elastic_cloud_location()}
            )
            self.elastic_cloud_id = secret_response.payload.data.decode("UTF-8")
            self.elastic_auth = get_elastic_auth()

        # Set up Elasticsearch client
        self.client: Elasticsearch = Elasticsearch(
            cloud_id=self.elastic_cloud_id,
            basic_auth=("elastic", self.elastic_auth),
            verify_certs=True,
            request_timeout=120
        )

    def ping(self):
        return self.client.ping()
    
    def search_documents(self, index, **kwargs):
        return self.client.search(index=index, **kwargs)
    