import json
import logging
import os
import uuid
from abc import ABCMeta, abstractmethod
from datetime import datetime
from functools import cached_property
from time import sleep

import requests
from airflow.configuration import conf
from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.utils.context import Context
from airflow.utils.decorators import apply_defaults

from ..macros import gcp

logger = logging.getLogger(name=__name__)


class BaseProcessor(metaclass=ABCMeta):
    @abstractmethod
    def pre_process(self):
        pass

    @abstractmethod
    def notebook_path(self):
        pass

    @abstractmethod
    def post_process(self):
        pass

    @staticmethod
    def generate_processor(input_nb: str):
        if input_nb.startswith("https://github.com"):
            return GitHubProcessor(input_nb=input_nb)
        else:
            return GCSProcessor(input_nb=input_nb)


class GitHubProcessor(BaseProcessor):
    def __init__(self, input_nb: str):
        self.input_nb = input_nb

    def pre_process(self) -> None:
        pass

    def notebook_path(self) -> str:
        return self.input_nb

    def post_process(self) -> None:
        pass


class GCSProcessor(BaseProcessor):
    def __init__(self, input_nb: str):
        self.input_nb = input_nb
        self._client = gcp.gcs_client()
        self._bucket = self._client.get_bucket("nes_notebooks_seoul_28d")
        self._filename = f"{datetime.now().date()}/{uuid.uuid4()}.ipynb"
        self._gcs_blob = self._bucket.blob(self._filename)
        self._dags_folder = conf.get("core", "dags_folder")

    def pre_process(self) -> None:
        self._gcs_blob.upload_from_filename(f"{self._dags_folder}/{self.input_nb}")

    def notebook_path(self) -> str:
        return f"gs://{self._bucket.name}/{self._filename}"

    def post_process(self) -> None:
        self._gcs_blob.delete()


class NesOperator(BaseOperator):
    template_fields = ("input_nb", "parameters")

    nes = "http://nes.sktai.io/v1/runs"
    poll_interval = 60
    run_id = None
    output_url = None

    @apply_defaults
    def __init__(
        self,
        input_nb: str,
        parameters: dict = None,
        runtime: str = None,
        profile: str = None,
        host_network: bool = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.input_nb = input_nb
        self.parameters = parameters
        self.runtime = runtime
        self.profile = profile
        self.host_network = host_network

    @cached_property
    def processor(self):
        return BaseProcessor.generate_processor(input_nb=self.input_nb)

    def pre_execute(self, context):
        self.processor.pre_process()

    def execute(self, context):
        def get_airflow_context() -> dict:
            return {
                "airflow_name": os.environ.get("AIRFLOW_NAME"),
                "airflow_dag_id": context["task"].dag_id,
                "airflow_task_id": context["task"].task_id,
                "airflow_owner": context["task"].owner,
            }

        def submit_job() -> tuple[str, str]:
            request_body = dict(
                input_url=self.processor.notebook_path(),
                parameters=self.parameters,
                runtime=self.runtime,
                profile=self.profile,
                host_network=self.host_network,
            )
            response = requests.post(
                url=self.nes,
                json=request_body,
                headers={
                    "Client-Id": "nes_operator",
                    "Client-Context": json.dumps(get_airflow_context()),
                },
            )
            logger.info(f"Job submitted with: {json.dumps(request_body)}")
            response.raise_for_status()
            response = response.json()
            return response["id"], response["output_url"]

        def get_status() -> str:
            response = requests.get(
                url=f"{self.nes}/{self.run_id}",
                headers={
                    "Client-Id": "nes_operator",
                    "Client-Context": json.dumps(get_airflow_context()),
                },
            )
            response.raise_for_status()
            response = response.json()
            return response["status"]

        self.run_id, self.output_url = submit_job()
        logger.info(
            f"""--------------------------------------------------------------------------------\n\n{self.output_url}\n\n--------------------------------------------------------------------------------"""
        )

        while (status := get_status()) != "Succeeded":
            sleep(self.poll_interval)
            logger.info(f'Polling job status... current status: "{status}"')
            if status in ["Failed", "Error", "NotFound"]:
                raise AirflowException(f'Job {self.run_id} exited with "{status}"')

        logger.info(f'Job {self.run_id} successfully finished with "{status}"')

    def post_execute(self, context: Context, result=None):
        self.processor.post_process()

    def on_kill(self):
        self.processor.post_process()

        while True:
            response = requests.delete(f"{self.nes}/{self.run_id}")
            status = response.json()["status"]
            logger.info(f'Deleting job... current status: "{status}"')
            if status in ["NotFound"]:
                break
            sleep(self.poll_interval)
