from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator
from datetime import datetime   


# Function for get_data task
def get_data(**kwargs):
    parser = argparse.ArgumentParser(
        description="Runs tests of Causal Effect under Partial-Observability."
    )
    parser.add_argument('file_path',
                        help='The path to the file you want to read'
    )
    parser.add_argument('-v', '--verbose', action='store_true', help="Show solver logs")
    args = parser.parse_args()

    # Creating a sample dictionary to pass
    data = {'key1': 'value1', 'key2': 'value2'}
    
    # Pushing the dictionary to XCom
    kwargs['ti'].xcom_push(key='data_dict', value=data)

# Function for solver_a task
def solver_a(**kwargs):
    # Pulling the dictionary from XCom (from the get_data task)
    data = kwargs['ti'].xcom_pull(task_ids='get_data', key='data_dict')
    
    # Now you can use the data in solver_a
    print(f"Data received in solver_a: {data}")

# Function for solver_b task (example)
def solver_b(**kwargs):
    data = kwargs['ti'].xcom_pull(task_ids='solver_a', key='data_dict')
    print(f"Data received in solver_b: {data}")

# Define the DAG
dag = DAG(
    'solver_pipeline_with_xcom',
    start_date=datetime(2023, 11, 14),
    schedule_interval=None,  # No periodic schedule
)

# Define tasks
get_data_task = PythonOperator(
    task_id='get_data',
    python_callable=get_data,
    provide_context=True,  # Ensure context is passed to the function
    dag=dag,
)

solver_a_task = PythonOperator(
    task_id='solver_a',
    python_callable=solver_a,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
get_data_task >> solver_a_task


# dag = DAG(
#     'solver_pipeline',
#     start_date=datetime(2023, 11, 14),
#     schedule_interval=None,
# )


# get_input_task = DockerOperator(
#     task_id='run_get_input',
#     image='get_input_image',
#     api_version='auto',
#     auto_remove=True,
#     dag=dag,
# )

# solver_dowhy_task = DockerOperator(
#     task_id='run_solver_dowhy',
#     image='solver_dowhy_image',
#     api_version='auto',
#     auto_remove=True,
#     dag=dag,
# )


# solver_bcause_task = DockerOperator(
#     task_id='run_solver_bcause',
#     image='solver_bcause_image',
#     api_version='auto',
#     auto_remove=True,
#     dag=dag,
# )


# solver_lcn_task = DockerOperator(
#     task_id='run_solver_lcn',
#     image='solver_lcn_image',
#     api_version='auto',
#     auto_remove=True,
#     dag=dag,
# )

# solver_autobounds_task = DockerOperator(
#     task_id='run_solver_autobounds',
#     image='solver_autobounds_image',
#     api_version='auto',
#     auto_remove=True,
#     dag=dag,
# )


# solver_dowhy_task >> solver_bcause_task >> solver_autobounds_task >> solver_lcn_task
