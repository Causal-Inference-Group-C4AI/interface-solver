def get_data(**kwargs):
    # Creating a sample dictionary to pass
    data = {'key1': 'value1', 'key2': 'value2'}
    
    # Pushing the dictionary to XCom
    kwargs['ti'].xcom_push(key='data_dict', value=data)

