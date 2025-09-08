import requests
import os
import json
from logging import getLogger
from log_config import logger_config
local_logger = getLogger(__name__)
logger_config(local_logger)


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
    local_logger.info('нашли базы данных')
    [local_logger.info(str(i)) for i in  datasets_ids]
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, 'databases_json.txt'), 'w', encoding='utf-8') as rt:
            rt.writelines(data_json)
    return data_json

def export_database(access_token, database_id, database_name, output_dir, superset_domain):
    dd = json.dumps([database_id])
    url = f"{superset_domain}/api/v1/database/export/?q={dd}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        os.makedirs(output_dir, exist_ok=True)
        file_name = database_name.replace("/", "_")
        zip_file_path = os.path.join(output_dir, f'database_{file_name}.zip')
        with open(zip_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        return zip_file_path
    else:
        local_logger.error(f"ошибка экспорта базы данных: {response.text}")

def del_database(access_token, database_id, superset_domain):
    local_logger.info(f"удаляем датасет {database_id}")
    url = f"{superset_domain}/api/v1/database/{database_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(url, headers=headers, stream=True)
    if response.status_code == 200:
        return True
    else:
        local_logger.error(f"ошибка убивания базы: {response.text}")

def create_database(access_token, database_name, engine, sqlalchemy_uri, superset_domain):
    url = f"{superset_domain}/api/v1/database/"
    jdata = {
        'configuration_method':'sqlalchemy_form',
        'database_name':database_name,
        'engine':engine,
        'sqlalchemy_uri':sqlalchemy_uri

    }
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(url, headers=headers, json=jdata)
    if response.status_code in [200, 201]:
        local_logger.info(f'успешно cоздание БД с парамсами {jdata}')
        return True
    else:
        local_logger.error(f'ошибка создания БД  {response.text}')
