import requests
import os
import json

def get_databases(access_token, output_dir, superset_domain):
    page=0
    per_page = 20
    downloaded = 0
    datasets_ids = []
    data_json = []
    while True:
        #url = f"{superset_domain}/api/v1/database/?q=(filters:!((col:database_name,opr:ct,value:'')),order_column:database_name,order_direction:asc,page:0,page_size:100)"
        url = f"{superset_domain}/api/v1/database/?q=(page:0,page_size:100)"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        resp_json = response.json()
        count = resp_json['count']
        new_dash = [(entity['id'], entity['database_name'], entity['uuid']) for entity in resp_json['result']]
        data_json.extend([json.dumps(rj, ensure_ascii=False)+'\n' for rj in resp_json['result']])
        downloaded = downloaded+len(new_dash)
        page+=1
        datasets_ids.extend(new_dash)
        if downloaded>=count:
            break
    print('нашли базы данных')
    [print(i[0],' ',i[1],' ',i[2]) for i in  datasets_ids]
    if output_dir:
        with open(os.path.join(output_dir, 'databases_json.txt'), 'w', encoding='utf-8') as rt:
            rt.writelines(data_json)
    return data_json

def export_database(access_token, datasets_id, dataset_name, output_dir, superset_domain):
    dd = json.dumps([datasets_id])
    url = f"{superset_domain}/api/v1/database/export/?q={dd}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        os.makedirs(output_directory, exist_ok=True)
        file_name = dataset_name.replace("/", "_")
        zip_file_path = os.path.join(output_dir, f'database_{file_name}.zip')
        with open(zip_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        return zip_file_path
    else:
        raise Exception(f"ошибка экспорта базы данных: {response.text}")

def del_database(access_token, database_id, superset_domain):
    url = f"{superset_domain}/api/v1/database/{database_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(url, headers=headers, stream=True)
    if response.status_code == 200:
        return True
    else:
        raise Exception(f"ошибка убивания базы: {response.text}")
