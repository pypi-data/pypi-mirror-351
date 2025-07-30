import datetime
import uuid

import pendulum
import pytest
from airflow.utils.state import DagRunState, TaskInstanceState
from airflow.utils.types import DagRunType

from airflow import DAG

from ..operators.v2.nes import CPURuntime, CPURuntimeSpec, NesOperator

DATA_INTERVAL_START = pendulum.datetime(2021, 9, 13, tz="UTC")
DATA_INTERVAL_END = DATA_INTERVAL_START + datetime.timedelta(days=1)

TEST_DAG_ID = f"nes_operator_dag_{str(uuid.uuid4())}"
TEST_TASK_ID = "nes_operator_task"


@pytest.fixture()
def dag():
    with DAG(
        dag_id=TEST_DAG_ID,
        schedule="@daily",
        start_date=DATA_INTERVAL_START,
    ) as dag:
        NesOperator(
            task_id=TEST_TASK_ID,
            runtime=CPURuntime(
                image="ye-basic-python3.8",
                tag="latest",
                spec=CPURuntimeSpec.LARGE,
            ),
            input_nb="https://github.com/sktaiflow/notebooks/blob/master/tests/operator_nes_test.ipynb",
            parameters={"KEY": "VALUE"},
        )
    return dag


def test_nes_operator(dag):
    dagrun = dag.create_dagrun(
        state=DagRunState.RUNNING,
        execution_date=DATA_INTERVAL_START,
        data_interval=(DATA_INTERVAL_START, DATA_INTERVAL_END),
        start_date=DATA_INTERVAL_END,
        run_type=DagRunType.MANUAL,
    )
    ti = dagrun.get_task_instance(task_id=TEST_TASK_ID)
    ti.task = dag.get_task(task_id=TEST_TASK_ID)
    ti.run(ignore_ti_state=True)
    assert ti.state == TaskInstanceState.SUCCESS
    # assert TaskInstanceState.SUCCESS == TaskInstanceState.SUCCESS
    # Assert something related to tasks results.
