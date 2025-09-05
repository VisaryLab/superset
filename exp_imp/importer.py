from subs.datasets import *
from subs.dashboards import *
from subs.auth import *
from subs.reports import *
from subs.database import *
from subs.charts import *
from subs.corrector import *
from subs.config import *

def get_clients_datasets(access_token, superset_domain):
    datasets = get_datasets(access_token, None, superset_domain)
    new_datasets = [json.loads(sl) for sl in datasets]
    return new_datasets

def get_clients_reports(access_token, superset_domain):
    reports = get_report_templates(access_token, None, superset_domain)
    new_reports = [json.loads(sl) for sl in reports]
    return new_reports

def get_clients_databases(access_token, superset_domain):
    databases = get_databases(access_token, None, superset_domain)
    new_databases = [json.loads(sl) for sl in databases]
    return new_databases

def get_clients_dashboards(access_token, superset_domain):
    dashboards = get_dashboards(access_token, None, superset_domain)
    new_dashboards = [json.loads(sl) for sl in dashboards]
    return new_dashboards

def get_clients_charts(access_token, superset_domain):
    charts = get_charts(access_token, None, superset_domain)
    new_charts = [json.loads(sl) for sl in charts]
    return new_charts

access_token, refresh_token = get_tokens()
# прочитаем сущности superset у заказчика

new_databases =  get_clients_databases(access_token, superset_domain)
new_datasets = get_clients_datasets(access_token, superset_domain)
new_dashboards =  get_clients_dashboards(access_token, superset_domain)
new_reports = get_clients_reports(access_token, superset_domain)
new_charts = get_clients_charts(access_token, superset_domain)


# следаем связку номенр отчета - id датасета из SS БА
full_ba_reports_ids = {}
with open(os.path.join(output_directory,'reports_json.txt'), 'r', encoding='utf-8') as f:
    all_ba_reports =f.readlines()
    for entity in all_ba_reports:
        dict_entity = json.loads(entity)
        full_ba_reports_ids[dict_entity.get('id')]={'dataset_id':dict_entity.get('dataset_id')}

ba_full_datasets = {} # словать uuid - id name датасетов БА
with open(os.path.join(output_directory,'datasets_json.txt'), 'r', encoding='utf-8') as f:
    jj =f.readlines()
    for entity in jj:
        dict_entity = json.loads(entity)
        ba_full_datasets[dict_entity.get('uuid')]={'id':dict_entity.get('id'), 'name':dict_entity.get('table_name')}

# список имен сущностей для удаления в SS заказчика
ba_datasets_names = []
ba_dashboards = []
ba_charts = []
ba_datasets_uuid =[]  # список uuid датасетов из zip архива - надо найти их ID

all_files = os.listdir(output_directory)
entity_to_proceed=[]
for one_file in all_files:
    if not one_file.startswith('dashboard'):
        continue
    if not one_file.endswith('zip'):
        continue
    entity_to_proceed.append(one_file)


for one_file in all_files:
    if not one_file.startswith('dataset'):
        continue
    if not one_file.endswith('zip'):
        continue
    entity_to_proceed.append(one_file)


# пробежим по всем дашбордам - вытащим все их сущности
for one_file in entity_to_proceed:#import_dashboards:
    params = get_db_params_zip(output_directory, one_file)
    if len(params['databases'])!=1:
        print(f"dashboard имеет не одну БД {len(params)}")

    if master_db!=params['databases'][0]['database_name']:
        continue


    datasets_from_zip = [ds["table_name"] for ds in params["datasets"]]
    #здесь защита от отдельного экспорта датасетов из дашборда
    for entity in datasets_from_zip:
        if entity in ba_datasets_names:
            continue

    ba_dashboards.extend([ds["dashboard_title"] for ds in params["dashboards"]])
    ba_datasets_names.extend([ds["table_name"] for ds in params["datasets"]]) # соберем все сущности из Аохива
    ba_datasets_uuid.extend([ds["uuid"] for ds in params["datasets"]]) #uuid dataset from zip
    ba_charts.extend([ds['slice_name'] for ds in params["charts"]])


    ba_datasets_names = list(set(ba_datasets_names))
    ba_dashboards = list(set(ba_dashboards))
    ba_charts = list(set(ba_charts))
    ba_datasets_uuid = list(set(ba_datasets_uuid))
    # список идишников на удаление
    delete_dataset = [entity['id'] for entity in new_datasets if entity["table_name"] in ba_datasets_names]
    delete_dashboards = [entity['id'] for entity in new_dashboards if entity["dashboard_title"] in ba_dashboards]
    delete_charts = [entity['id'] for entity in new_charts if entity["slice_name"] in ba_charts]

    ba_dataset_from_zip=[ba_full_datasets[entity]['id'] for entity in ba_datasets_uuid if entity in ba_full_datasets]# по uuid найдем Id датасетов  из zip файлов

    ba_dataset_id_to_delete =[full_ba_reports_ids[entity]['dataset_id'] for entity in full_ba_reports_ids if full_ba_reports_ids[entity]['dataset_id'] in ba_dataset_from_zip] # найдем id датасетов у которые точно есть репорты из ZIP файдла

    name_dataset_to_delete_report =[ba_full_datasets[entity]['name'] for entity in ba_full_datasets if ba_full_datasets[entity]['id'] in  ba_dataset_id_to_delete] #получим список имен датасетов у которых есть отчеты

    dataset_with_reports_id = [entity['id'] for entity in new_datasets if entity['table_name'] in name_dataset_to_delete_report] # по именам найдем id датасетов у заказчика у который могут быть отчеты у

    reports_to_delete=[entity['id'] for entity in new_reports if entity['dataset_id'] in dataset_with_reports_id] #по id дасетов взаказчика найдетм id репортов которые надо дропнуть

    # дропаем
    [del_charts(access_token, entity, superset_domain)  for entity in delete_charts]
    [del_dashboard(access_token, entity, superset_domain)  for entity in delete_dashboards]
    [del_dataset(access_token, entity, superset_domain)  for entity in delete_dataset]
    [del_report(access_token, entity, superset_domain)  for entity in reports_to_delete]

    #экспорт
    #for one_file in entity_to_proceed:
    #params = get_db_params_zip(output_directory, one_file)
    uri = client_database[0]['sqlalchemy_uri']
    uuid = client_database[0]['uuid']
    database_name = client_database[0]['database_name']
    if len(params['databases'])!=1:
        print(f"dashboard имеет не одну БД {len(params)}")
        exit(1)
    zip_corrector(sqlalchemy_uri= uri, database_uuid=uuid, database_name=database_name, output_dir=output_directory, zip_file=one_file)
    if "dashboard" in one_file:
        import_dashboard(access_token, os.path.join(output_directory, one_file), superset_domain)
    elif "dataset" in one_file:
        import_dataset(access_token, os.path.join(output_directory, one_file), superset_domain)


dataset_reports=[]
#обновим id датасетов
new_datasets = get_clients_datasets(access_token, superset_domain)
# идем по списку всех репортов
for entity in all_ba_reports:
    dict = json.loads(entity) #загрузим 1 репорт
    dataset_id = dict['dataset_id']
    desc = dict['description']
    name = dict['name']
    id = dict['id']
    table_name, table_id = None,None

    for table_uuid in ba_full_datasets:
        if ba_full_datasets[table_uuid]['id']==dataset_id:  # dataset_id найден в словаре датасетов
            table_name = ba_full_datasets[table_uuid]['name']
            break

    # найдем id в новом SS заказчика по имени
    new_id = None
    for new_entity in new_datasets:
        if new_entity['table_name']==table_name: # нашли таблю по имени в ss заказчика
            new_id = new_entity['id']
            output_file = os.path.join(output_directory, 'report_template_' + name + '.odt')
            if new_id:
                import_report_template(access_token, new_id, output_file, desc, superset_domain)
exit(1)



#---------------------------------------------------------------------------------------------------------------------
