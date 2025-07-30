from airflow.sensors.base import BaseSensorOperator

from ..macros.gcp import bigquery_client


class BigqueryPartitionSensor(BaseSensorOperator):
    template_fields = ("dataset_id", "table_id", "partition")

    def __init__(
        self,
        dataset_id,
        table_id,
        partition,
        timeout=(60 * 60) * 24 * 2,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.project_id = "skt-datahub"
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.partition = partition
        self.mode = "reschedule"
        self.poke_interval = 300  # 5 min
        self.timeout = timeout

    def poke(self, context):
        sql = f"select '42' from `{self.project_id}.{self.dataset_id}.{self.table_id}` where {self.partition} limit 1"
        return bigquery_client().query(sql).result().total_rows > 0
