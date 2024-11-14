import argparse
import logging


from input_processor import InputProcessor
from interface import interface


def pipeline(input_path: str):
    input_processor = InputProcessor(input_path)







if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs tests of Causal Effect under Partial-Observability."
    )
    parser.add_argument('file_path',
                        help='The path to the file you want to read'
    )
    parser.add_argument('-v', '--verbose', action='store_true', help="Show solver logs")
    args = parser.parse_args()
    try:
        if not args.verbose:
            logging.getLogger().setLevel(logging.CRITICAL)
        pipeline(args.file_path)
    except Exception as e:
        print(f"{type(e).__module__}.{type(e).__name__}: {e}")




from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator
from datetime import datetime

# Define the DAG
dag = DAG(
    'plus_operator_pipeline',
    start_date=datetime(2023, 11, 14),
    schedule_interval=None,  # No periodic schedule
)

# Define the task that runs plus_operator in Docker container
def run_plus_operator(a, b, **kwargs):
    # Use XCom to pass parameters a and b to the DockerOperator
    return {
        'a': a,
        'b': b
    }

# Task to trigger the plus_operator function inside Docker container
plus_operator_task = DockerOperator(
    task_id='plus_operator_task',
    image='plus-operator-image',  # The Docker image containing the plus_operator function
    api_version='auto',
    auto_remove=True,
    command="python /app/plus_operator.py {{ task_instance.xcom_pull(task_ids='run_plus_operator')['a'] }} {{ task_instance.xcom_pull(task_ids='run_plus_operator')['b'] }}",  # Pass a and b to the Python script
    volumes=["/path/to/output:/output"],  # Mount the local output directory to the container's /output folder
    dag=dag,
)

# Task to dynamically provide input a and b (could be from an external source, or hardcoded for now)
run_plus_operator_task = PythonOperator(
    task_id='run_plus_operator',
    python_callable=run_plus_operator,
    op_args=[5, 3],  # Example values for a and b
    provide_context=True,
    dag=dag,
)

# Set the task dependencies
run_plus_operator_task >> plus_operator_task
