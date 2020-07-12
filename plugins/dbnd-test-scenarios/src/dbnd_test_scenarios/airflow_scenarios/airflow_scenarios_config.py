import inspect
import os

from airflow import DAG
from airflow.utils.dates import days_ago

from dbnd._core.inplace_run.airflow_utils import track_dag
from dbnd._core.utils.basics.helpers import parse_bool

start_days_ago = int(os.environ.get("SCENARIOS__START_DAYS_AGO", "2"))
catchup = parse_bool(os.environ.get("SCENARIOS__CATCHUP", "False"))
output_root = os.environ.get("SCENARIOS__OUTPUT_ROOT", "/tmp/staging/outputs")

DEFAULT_ARGS = {
    "owner": "staging",
    "start_date": days_ago(start_days_ago),
    "catchup": catchup,
}


def dag_task_output(*path):
    return os.path.join(output_root, *path)


def dag_task_output_partition_csv(name):
    return dag_task_output("%s.{{ds}}.csv", name)


def txcom(task_id):
    return "{{ti.xcom_pull(task_ids='%s')}}" % task_id


class SmartScheduler(object):
    frequent = "*/15 * * * *"
    daily = "0 1 * * *"  # daily at 1am


stg_schedule = SmartScheduler()


def magicDAG(dag_id, **kwargs):
    # make sure that created dag is visible at the place of creation
    # so user doesn't need to assign it to variable (global) on module level
    # HINT: Airflow discover dags by looking ag globals() of imported module
    # and taking all variables with DAG instance
    caller_globals = inspect.stack()[1][0].f_globals

    kwargs.setdefault("default_args", DEFAULT_ARGS)
    kwargs.setdefault("schedule_interval", SmartScheduler.daily)
    # catchup
    # tracking
    dag = TrackedDAG(dag_id=dag_id, **kwargs)

    # set dag at global space so it can be discovered
    caller_globals["DAG__%s" % dag_id] = dag
    return dag


class TrackedDAG(DAG):
    """
    Use only as `with TrackedDAG():`
    """

    def __exit__(self, _type, _value, _tb):
        super(TrackedDAG, self).__exit__(_type, _value, _tb)
        track_dag(self)
