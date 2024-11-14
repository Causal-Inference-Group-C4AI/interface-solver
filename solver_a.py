def solver_a(**kwargs):
    # Pulling the dictionary from XCom (from the get_data task)
    data = kwargs['ti'].xcom_pull(task_ids='get_data', key='data_dict')
    
    # Now you can use the data in solver_a
    print(f"Data received in solver_a: {data}")

