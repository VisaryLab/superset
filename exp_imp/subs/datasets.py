import requests
import os
import json

def get_datasets(access_token, output_dir, superset_domain):
    page=0
    per_page = 20
    downloaded = 0
    datasets_ids = []
    data_json = []
    while True:
        url = f"{superset_domain}/api/v1/dataset/?q=(page:{page},page_size:{per_page})"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        resp_json = response.json()
        count = resp_json['count']
        data_json.extend([json.dumps(rj, ensure_ascii=False)+'\n' for rj in resp_json['result']])
        new_dash = [(entity['id'], entity['table_name']) for entity in resp_json['result']]
        downloaded = downloaded+len(new_dash)
        page+=1
        datasets_ids.extend(new_dash)
        if downloaded>=count:
            break
    if output_dir:
        with open(os.path.join(output_dir, 'datasets_json.txt'), 'w', encoding='utf-8') as rt:
            rt.writelines(data_json)
    print('нашли датасеты')
    [print(i[0],' ',i[1]) for i in  datasets_ids]
    return data_json

def export_dataset(access_token, datasets_id, dataset_name, output_dir, superset_domain):
    url = f"{superset_domain}/api/v1/dataset/export/?q={json.dumps([datasets_id])}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        os.makedirs(output_dir, exist_ok=True)
        file_name = dataset_name.replace("/", "_")
        zip_file_path = os.path.join(output_dir, f'dataset_{file_name}.zip')
        with open(zip_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        return zip_file_path
    else:
        raise Exception(f"ошибка экспорта датасета: {response.text}")


def import_dataset(access_token, output_dir, superset_domain):
    url = f"{superset_domain}/api/v1/dataset/import/"
    _, filename = os.path.split(output_dir)
    headers = {'Authorization': f'Bearer {access_token}' }

    files = {'formData': (filename, open(output_dir, 'rb'),"application/x-zip-compressed" ),
             "passwords": (None,"{}"),
             "ssh_tunnel_passwords": (None,"{}"),
             "ssh_tunnel_private_keys": (None,"{}"),
             "ssh_tunnel_private_key_passwords": (None,"{}"),
             "overwrite": (None,"true"),
             "sync_columns": (None,"false"),
             "sync_metrics": (None,"false")
             }
    response = requests.post(url, headers=headers, files=files)
    if response.status_code==200:
        print('загрузили ')
    else:
        f = response.text
        raise Exception(f"ошибка экспорта датасета: {f}")

def del_dataset(access_token, datasets_id, superset_domain):
    url = f"{superset_domain}/api/v1/dataset/{datasets_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(url, headers=headers, stream=True)
    if response.status_code == 200:
        return True
    else:
        print(f"ошибка убивания датасета: {response.text}")
