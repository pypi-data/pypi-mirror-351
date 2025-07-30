# apache-airflow-providers-sktvane

- AIDP 가 제공하는 자원들에 접근하는 용도
  - `NES`
  - `BigQuery`
  - `Vault`
- 기타 공용 목적의 코드

## PyPI

- https://pypi.org/project/apache-airflow-providers-sktvane

## Environments

### Local

* `VAULT_TOKEN` 은 [관련 문서](https://www.notion.so/ai-data-engineering/Public-3ec3cd8a4e444aa38a6f02fe57e3b6bd?pvs=4#c0b08e2b147f4e0383c67cedadbb0bdc) 에서 확인
  ```shell
  export VAULT_ADDR=https://vault-public.sktai.io
  export VAULT_TOKEN={{VAULT_TOKEN}}
  export AIRFLOW__CORE__DAGS_FOLDER=.
  ```

## Deployment

* `main` 브랜치에 `push` 이벤트 발생 시 배포, 부득이하게 로컬 환경에서 배포할 경우 아래 명령 수행
    ```shell
    # build
    $ python setup.py sdist bdist_wheel
    # upload
    $ twine upload dist/*
    # remove
    $ rm -rf build dist apache_airflow_providers_sktvane.egg-info 
    ```

## Components

###### Operators

- `airflow.providers.sktvane.operators.nes.NesOperator` : AIDP 의 `NES` 사용
    ```python
    from airflow.providers.sktvane.operators.nes import NesOperator
    
    ...
    
    NesOperator(
        task_id="jupyter_daily_count",
        input_nb="https://github.com/sktaiflow/notebooks/blob/master/statistics/jupyter_daily_count.ipynb",
        parameters={"current_date": "{{ ds }}", "channel": "#aim-statistics"},
    )
    ```
        

###### Sensors

- `airflow.providers.sktvane.sensors.gcp.BigqueryPartitionSensor` : AIDP 의 `BigQuery` 파티션 체크

    ```python
    from airflow.providers.sktvane.sensors.gcp import BigqueryPartitionSensor
    
    ...
    
    BigqueryPartitionSensor(
        task_id=f"{table}_partition_sensor",
        dataset_id="wind_tmt",
        table_id=table,
        partition="dt = '{{ds}}'",
    )
    ``` 

###### Macros

- `airflow.providers.sktvane.macros.slack.send_fail_message` : AIDP 정의 포맷으로 `Slack` 에러 메시지 발송
    ```python
    from airflow.providers.sktvane.macros.slack import send_fail_message
    
    ...
    
    def send_aidp_fail_message(slack_email: str) -> None:
      send_fail_message(
        slack_channel="#aidp-airflow-monitoring",
        slack_username=f"Airflow-AlarmBot-{env}",
        slack_email=slack_email,
      )
    ```
        
- `airflow.providers.sktvane.macros.gcp.bigquery_client` : AIDP 의 `BigQuery` 사용
    ```python
    from airflow.providers.sktvane.macros.gcp import bigquery_client
    
    ...
    
    def bq_query_to_bq(query, dest_table_name, **kwarg):
      bq_client = bigquery_client()
      job = bq_client.query(query)
      job.result()
    ```
        
- `airflow.providers.sktvane.macros.vault.get_secrets` : AIDP 의 `Vault` 사용
    ```python
    from airflow.providers.sktvane.macros.vault import get_secrets
    
    ...
    
    def get_hive_conn():
      from pyhive import hive
    
      hiveserver2 = get_secrets(path="ye/hiveserver2")
      host = hiveserver2["ip"]
      port = hiveserver2["port"]
      user = hiveserver2["user"]
      conn = hive.connect(host, port=port, username=user)
      return conn
    ```
        
- `airflow.providers.sktvane.macros.date.ds_nodash_plus_days` : AIDP 에서 제공하는 `date` 유틸리티
    ```python
    from airflow.providers.sktvane.macros.date import ds_nodash_plus_days
    
    ...
    
    def ds_nodash_tomorrow(ds):
        ds_nodash_plus_days(ds, 1)
    ```
- `airflow.providers.sktvane.macros.date.ds_nodash_minus_days` : `ds_nodash_plus_days` 와 동일
- `airflow.providers.sktvane.macros.date.ym_nodash_add_month` : `ds_nodash_plus_days` 와 동일
- `airflow.providers.sktvane.macros.date.first_day_of_this_month` : `ds_nodash_plus_days` 와 동일
- `airflow.providers.sktvane.macros.date.last_day_of_this_month` : `ds_nodash_plus_days` 와 동일
- `airflow.providers.sktvane.macros.date.get_latest_loaded_dt` : `ds_nodash_plus_days` 와 동일
