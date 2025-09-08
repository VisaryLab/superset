import requests
import os
import json
from logging import getLogger
from log_config import logger_config
local_logger = getLogger(__name__)
logger_config(local_logger)

def get_dashboards(access_token, output_dir, superset_domain):
    page=0
    per_page = 20
    downloaded = 0
    dashboard_ids = []
    data_json = []
    while True:
        url = f"{superset_domain}/api/v1/dashboard/?q=(page:{page},page_size:{per_page})"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        resp_json = response.json()
        count = resp_json['count']
        new_dash = [(entity['id'], entity['dashboard_title']) for entity in resp_json['result']]
        data_json.extend([json.dumps(rj , ensure_ascii=False)+'\n' for rj in resp_json['result']])
        downloaded = downloaded+len(new_dash)
        page+=1
        dashboard_ids.extend(new_dash)
        if downloaded>=count:
            break
    local_logger.info('нашли дашборды')
    [local_logger.info(str(i)) for i in dashboard_ids]
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, 'dashboard_json.txt'), 'w', encoding='utf-8') as rt:
            rt.writelines(data_json)
    return data_json

def export_dashbord(access_token, dashboard_id, dashboard_name, output_dir, superset_domain):
    url = f"{superset_domain}/api/v1/dashboard/export/?q={json.dumps([dashboard_id])}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        os.makedirs(output_dir, exist_ok=True)
        file_name = dashboard_name.replace("/", "_")
        zip_file_path = os.path.join(output_dir, f'dashboard_{file_name}.zip')
        with open(zip_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        return zip_file_path
    else:
        local_logger.error(f"ошибка экспорта дашборда: {response.text}")


def export_dashbord_json(access_token, dashboard_id, dashboard_name, output_dir, superset_domain):
    url = f"{superset_domain}/api/v1/dashboard/{dashboard_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        os.makedirs(output_dir, exist_ok=True)
        file_name = dashboard_name.replace("/", "_")
        zip_file_path = os.path.join(output_dir, f'dashboard_{file_name}.json')
        with open(zip_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        return zip_file_path
    else:
        local_logger.error(f"ошибка экспорта дашборда: {response.text}")



def import_dashboard(access_token, output_dir, superset_domain):
    url = f"{superset_domain}/api/v1/dashboard/import/"
    _, filename = os.path.split(output_dir)
    headers = {'Authorization': f'Bearer {access_token}' }

    files = {'formData': (filename, open(output_dir, 'rb'),"application/x-zip-compressed" ),
             "passwords": (None,"{}"),
             "ssh_tunnel_passwords": (None,"{}"),
             "ssh_tunnel_private_keys": (None,"{}"),
             "ssh_tunnel_private_key_passwords": (None,"{}"),
             "overwrite": (None,"true"),
             }
    response = requests.post(url, headers=headers, files=files)#, data=formData)
    if response.status_code==200:
        print('загрузили ')
    else:
        f = response.text
        local_logger.error(f"ошибка импорта дашборда: {f}")


def del_dashboard(access_token, dashboard_id, superset_domain):
    local_logger.info(f"удаляем датасет {dashboard_id}")
    url = f"{superset_domain}/api/v1/dashboard/{dashboard_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(url, headers=headers, stream=True)
    if response.status_code == 200:
        return True
    else:
        local_logger.error(f"ошибка убивания дашборда: {response.text}")
