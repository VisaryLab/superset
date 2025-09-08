import requests
import os
import json
from logging import getLogger
from log_config import logger_config
local_logger = getLogger(__name__)
logger_config(local_logger)


def get_css_templates(access_token, output_dir, superset_domain):
    page=0
    per_page = 20
    downloaded = 0
    dashboard_ids = []
    dashboard_ids = []
    data_json = []
    while True:
        url = f"{superset_domain}/api/v1/css_template/?q=(page:{page},page_size:{per_page})"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        resp_json = response.json()
        count = resp_json['count']
        new_dash = [(entity['id'], entity['template_name']) for entity in resp_json['result']]
        data_json.extend([json.dumps(rj, ensure_ascii=False) + '\n' for rj in resp_json['result']])
        downloaded = downloaded+len(new_dash)
        page+=1
        dashboard_ids.extend(new_dash)
        if downloaded>=count:
            break
    local_logger.info('нашли css')
    [local_logger.info(str(i)) for i in dashboard_ids]
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, 'css_json.txt'), 'w', encoding='utf-8') as rt:
            rt.writelines(data_json)
    return data_json


def export_css_template(access_token, css_template_id, css_template_name, output_dir, superset_domain):
    local_logger.info(f"удаляем датасет {css_template_id}")
    url = f"{superset_domain}/api/v1/css_template/{css_template_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        os.makedirs(output_dir, exist_ok=True)
        file_name = css_template_name.replace("/", "_")
        zip_file_path = os.path.join(output_dir, f'css_template_{file_name}.txt')
        with open(zip_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        return zip_file_path
    else:
        raise Exception(f"ошибка экспорта дашборда: {response.text}")

def import_css_template(access_token, output_dir, superset_domain):
    url = f"{superset_domain}/api/v1/dashboard/import/"
    _, filename = os.path.split(output_dir)
    headers = {'Authorization': f'Bearer {access_token}' }

    css_json = {"css":"345345342",  "template_name":"1234"}  #ВЗЯТЬ ИЗ ФАЙЛА ЧТОЛДИ???
    response = requests.post(url, headers=headers, json=css_json)#, data=formData)
    if response.status_code==200:
        print('загрузили ')
    else:
        f = response.text
        raise Exception(f"ошибка экспорта датасета: {f}")


def del_css_template(access_token, css_template_id, superset_domain):
    url = f"{superset_domain}/api/v1/css_template/{css_template_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(url, headers=headers, stream=True)
    if response.status_code == 200:
        return True
    else:
        raise Exception(f"ошибка убивания css: {response.text}")
