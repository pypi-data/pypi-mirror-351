from datetime import datetime, timedelta

from airflow.exceptions import AirflowException
from dateutil.relativedelta import relativedelta


def ds_nodash_plus_days(ds, days):
    ds = datetime.strptime(ds, "%Y%m%d")
    ds = ds + timedelta(days)
    return ds.strftime("%Y%m%d")


def ds_nodash_minus_days(ds, days):
    ds = datetime.strptime(ds, "%Y%m%d")
    ds = ds - timedelta(days)
    return ds.strftime("%Y%m%d")


def ym_nodash_add_month(ds, months, prev_ds=True):
    ds = datetime.strptime(ds, "%Y%m%d")
    time_delta = timedelta(-1) if prev_ds else timedelta(0)
    ds = ds + time_delta + relativedelta(months=months)
    return ds.strftime("%Y%m")


def first_day_of_last_month(ds):
    date = datetime.strptime(ds, "%Y%m%d")
    dt = date.replace(month=date.month, day=1) - timedelta(days=1)
    return dt.replace(month=dt.month, day=1).strftime("%Y%m%d")


def last_day_of_last_month(ds):
    date = datetime.strptime(ds, "%Y%m%d")
    dt = date.replace(month=date.month, day=1) - timedelta(days=1)
    return dt.strftime("%Y%m%d")


def first_day_of_this_month(ds):
    date = datetime.strptime(ds, "%Y%m%d")
    dt = date.replace(month=date.month, day=1)
    return dt.strftime("%Y%m%d")


def last_day_of_this_month(ds):
    date = datetime.strptime(ds, "%Y%m%d") + relativedelta(months=1)
    dt = date.replace(month=date.month, day=1) - timedelta(days=1)
    return dt.strftime("%Y%m%d")


def get_latest_loaded_dt(find_before, table_name, schema="saturn"):
    from airflow.providers.apache.hive.hooks.hive import HiveMetastoreHook as Hook

    partitions = Hook().get_partitions(schema=schema, table_name=table_name)
    dts = [p.get("dt") for p in partitions if p.get("dt") < str(find_before)]

    if not dts:
        raise AirflowException(
            f'Get latest dt FAIL: "{table_name}" has no previously loaded dt'
        )

    return max(dts)
