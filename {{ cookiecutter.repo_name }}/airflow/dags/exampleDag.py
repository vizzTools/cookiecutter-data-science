import airflow  # noqa

from datetime import timedelta

from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

from airflow.processors.processors import (DownloadFileProcessor)

FILENAME = 'result.csv'
DESTINATION_PATH = '/tmp/'
DESTINATION_FILE = f'{DESTINATION_PATH}/{FILENAME}'

args = {'owner': 'airflow', 'start_date': airflow.utils.dates.days_ago(2)}

dag = DAG(dag_id='test',
          default_args=args,
          dagrun_timeout=timedelta(minutes=60))

start = DummyOperator(task_id='start', dag=dag)

download_processor = DownloadFileProcessor(
    url='https://github.com/openmundi/world.csv/raw/master/countries(204)\
    _olympics.csv',
    filename=FILENAME,
    path=DESTINATION_PATH)
download = PythonOperator(task_id='download_csv',
                          python_callable=download_processor.run,
                          dag=dag)
download.set_upstream(start)
