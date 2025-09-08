import requests
import os
import json
from logging import getLogger
from log_config import logger_config
local_logger = getLogger(__name__)
logger_config(local_logger)


def get_charts(access_token, output_dir, superset_domain):
    page=0
    per_page = 20
    downloaded = 0
    charts_ids = []
    data_json = []
    while True:
        url = f"{superset_domain}/api/v1/chart/?q=(page:{page},page_size:{per_page})"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        resp_json = response.json()
        count = resp_json['count']
        data_json.extend([json.dumps(rj, indent=4, ensure_ascii=False)+'\n' for rj in resp_json['result']])
        new_chart = [(entity['id'], entity['slice_name']) for entity in resp_json['result']]
        downloaded = downloaded+len(new_chart)
        page+=1
        charts_ids.extend(new_chart)
        if downloaded>=count:
            break
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, 'charts_json.txt'), 'w', encoding='utf-8') as rt:
            rt.writelines(data_json)
    local_logger.info('нашли чарты')
    [local_logger.info(str(i)) for i in charts_ids]
    return data_json

def export_chart(access_token, chart_id, chart_name, output_dir, superset_domain):
    url = f"{superset_domain}/api/v1/chart/export/?q={json.dumps([chart_id])}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        os.makedirs(output_dir, exist_ok=True)
        file_name = chart_name.replace("/", "_")
        zip_file_path = os.path.join(output_dir, f'chart_{file_name}.zip')
        print(zip_file_path)
        try:
            with open(zip_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=128):
                   f.write(chunk)
            return zip_file_path
        except Exception as e:
            print(e)
    else:
        pass

def import_chart(access_token, output_dir, superset_domain):
    url = f"{superset_domain}/api/v1/chart/import/"
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
        print(f"ошибка импорта чарта: {f}")

def del_charts(access_token, chart_id, superset_domain):
    local_logger.info(f"удаляем чарт {chart_id}")
    url = f"{superset_domain}/api/v1/chart/{chart_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(url, headers=headers, stream=True)
    if response.status_code == 200:
        return True
    else:
        print(f"ошибка убивания chart: {response.text}")
