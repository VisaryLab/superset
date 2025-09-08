import requests
import os
import json
from logging import getLogger
from log_config import logger_config
local_logger = getLogger(__name__)
logger_config(local_logger)

def get_report_templates(access_token, output_dir, superset_domain):
    limit=20
    offset=0
    downloaded = 0
    reports_ids = []
    data_json = []
    while True:
        url = f"{superset_domain}/api/v1/report_template/?limit={limit}&offset={offset}"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        resp_json = response.json()
        data_json.extend([json.dumps(rj, ensure_ascii=False)+'\n' for rj in resp_json['result']])
        count = resp_json['count']
        new_dash = [(entity['id'], entity['name'], entity['dataset_id']) for entity in resp_json['result']]
        downloaded = downloaded+len(new_dash)
        offset+=limit
        reports_ids.extend(new_dash)
        if downloaded>=count:
            break
    local_logger.info('нашли отчеты')
    [local_logger.info(str(i)) for i in reports_ids]
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, 'reports_json.txt'), 'w', encoding='utf-8') as rt:
            rt.writelines(data_json)
    return data_json

def export_report_template(access_token, report_template_id, report_template_name, output_dir, superset_domain):
    url = f"{superset_domain}/api/v1/report_template/{report_template_id}/download"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        os.makedirs(output_dir, exist_ok=True)
        file_name = report_template_name.replace("/", "_")
        extension = response.headers['Content-Disposition'].lower()
        filename = extension.split('filename=')[1]
        ext = filename.split('.')[1].strip()
        zip_file_path = os.path.join(output_dir, f'report_template_{file_name}.{ext}')
        with open(zip_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        return zip_file_path
    else:
        local_logger.error(f"ошибка экспорта дашборда: {response.text}")


def import_report_template(access_token, dataset_id, output_dir, desc, superset_domain):  # имя датасет описание сам файл
    url = f"{superset_domain}/api/v1/report_template/"
    _, filename = os.path.split(output_dir)
    headers = {'Authorization': f'Bearer {access_token}' }
    name = filename.replace('report_template_', '')
    files = {'template': (filename, open(output_dir, 'rb'),"application/vnd.oasis.opendocument.text" ),
             "name": (None, name),
             "dataset_id": (None, str(dataset_id)),
             'description':(None, str(desc))
             }


    response = requests.post(url, headers=headers, files=files)
    if response.status_code in [200, 201]:
        print('загрузили ')
    else:
        f = response.text
        local_logger.error(f"ошибка экспорта репорта: {f}")

def del_report(access_token, report_id, superset_domain):
    url = f"{superset_domain}/api/v1/report_template/{report_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(url, headers=headers, stream=True)
    if response.status_code == 200:
        return True
    else:
        local_logger.error(f"ошибка убивания репорта: {response.text}")
