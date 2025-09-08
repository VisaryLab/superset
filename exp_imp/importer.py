from subs.datasets import *
from subs.dashboards import *
from subs.auth import *
from subs.reports import *
from subs.database import *
from subs.charts import *
from subs.corrector import *
from subs.config import *

from logging import getLogger
from log_config import logger_config
local_logger = getLogger("importer")
logger_config(local_logger)
database_logger = getLogger("subs.database")
logger_config(database_logger)



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



access_token, refresh_token = get_tokens(superset_domain, connect_params)
# прочитаем сущности superset у заказчика
local_logger.info('получим сущности SS у заказчика')
new_databases =  get_clients_databases(access_token, superset_domain)
local_logger.info(f"Найдено  {len(new_databases)} баз данных")

new_datasets = get_clients_datasets(access_token, superset_domain)
local_logger.info(f"Найдено  {len(new_datasets)} баз датасетов")

new_dashboards =  get_clients_dashboards(access_token, superset_domain)
local_logger.info(f"Найдено  {len(new_dashboards)} дашбордов")

new_reports = get_clients_reports(access_token, superset_domain)
local_logger.info(f"Найдено  {len(new_reports)} шаблонов отчетов")

new_charts = get_clients_charts(access_token, superset_domain)
local_logger.info(f"Найдено  {len(new_charts)} чартов")


local_logger.info(f"загрузим список шаблонов отчетов из БА")
# следаем связку номенр отчета - id датасета из SS БА
full_ba_reports_ids = {}
with open(os.path.join(output_directory,'reports_json.txt'), 'r', encoding='utf-8') as f:
    all_ba_reports =f.readlines()
    for entity in all_ba_reports:
        dict_entity = json.loads(entity)
        full_ba_reports_ids[dict_entity.get('id')]={'dataset_id':dict_entity.get('dataset_id')}

local_logger.info(f"загрузим список датасетов из БА")
ba_full_datasets = {} # словать uuid - id name датасетов БА
with open(os.path.join(output_directory,'datasets_json.txt'), 'r', encoding='utf-8') as f:
    jj =f.readlines()
    for entity in jj:
        dict_entity = json.loads(entity)
        ba_full_datasets[dict_entity.get('uuid')]={'id':dict_entity.get('id'), 'name':dict_entity.get('table_name')}
# Здесь разберемся с коннектами к бд
ba_database = []
all_files = os.listdir(output_directory)
database_to_proceed=[]
for one_file in all_files:
    if not one_file.startswith('database'):
        continue
    if not one_file.endswith('zip'):
        continue
    database_to_proceed.append(one_file)
for one_file in database_to_proceed:
    params = get_db_params_zip(output_directory, one_file)
    ba_database.append({'database_name':params['databases'][0]['database_name'], 'sqlalchemy_uri':params['databases'][0]['sqlalchemy_uri'], 'uuid':params['databases'][0]['uuid']})
local_logger.info(f'Найдены БД для экспорта {ba_database}')
print('приготовьте пароли для создания коннекта к БД заказчик')
# найдем БД для переноса  - по именам которых нет у заказчика
new_database_names = [entity['database_name'] for entity in new_databases]
db_name_to_create = [entity for entity in ba_database if entity['database_name'] not in new_database_names]
for entity in db_name_to_create:
    passs = input(f"для {entity['database_name']} дайте пароль")
    if passs!='':
        client_sqlalchemy_uri = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(export_pg['user'], passs, export_pg['host'], export_pg['port'], entity['database_name'])
    #    create_database(access_token, entity['database_name'], client_sqlalchemy_engine, client_sqlalchemy_uri , superset_domain)
    else:
        print('пропустим создание - нет пароля')
#сморим что получилсь
local_logger.info('сохраним БД заказчика в файлы')
client_database = []
#for a in  get_databases(access_token, tmp_directory , superset_domain):
#    b = json.loads(a)
#    id = b['id']
#    name = b['database_name']
#    local_logger.info(f'сохраним zip м описанием базы {name}')
#    export_database(access_token, id, name, tmp_directory , superset_domain)

new_databases =  get_clients_databases(access_token, superset_domain)
for entity in new_databases:
    user = export_pg['user']
    dbn = entity['database_name']
    passs = input(f"дайте пароль для пользоователя {user} для нужных БД {dbn} только типа Postgresql")
    if passs:
        sqlalchemy_uri = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(export_pg['user'], passs, export_pg['host'],
                                                                          export_pg['port'], entity['database_name'])
        client_database.append({'database_name': entity['database_name'],
                            'sqlalchemy_uri': sqlalchemy_uri,
                            'uuid': entity['uuid']})


# список имен сущностей для удаления в SS заказчика
ba_datasets_names = []
ba_dashboards = []
ba_charts = []
ba_datasets_uuid =[]  # список uuid датасетов из zip архива - надо найти их ID
local_logger.info("найдем все дашборды и датасеты экспортируемые из БА")
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

common_ba_dataset_names = []

# пробежим по всем дашбордам - вытащим все их сущности
for one_file in entity_to_proceed:#import_dashboards:
    local_logger.info(f'обрабатываем сущность {one_file}')
    params = get_db_params_zip(output_directory, one_file)
    local_logger.info(f'сущность имеет параметры {params}')
    if len(params['databases'])!=1:
        print(f"dashboard имеет не одну БД {len(params)}")

    if params['databases'][0]['database_name'] not in master_db:
        continue

    database_from_zip = params['databases'][0]['database_name']
    datasets_from_zip = [ds["table_name"] for ds in params["datasets"]]
    #здесь защита от отдельного экспорта датасетов из дашборда
    for entity in datasets_from_zip:
        if entity in common_ba_dataset_names:
            continue

    ba_dashboards=[ds["dashboard_title"] for ds in params["dashboards"]]
    ba_datasets_names = [ds["table_name"] for ds in params["datasets"]]# соберем все сущности из Аохива
    ba_datasets_uuid  =[ds["uuid"] for ds in params["datasets"]] #uuid dataset from zip
    ba_charts = [ds['slice_name'] for ds in params["charts"]]

    ba_datasets_names = list(set(ba_datasets_names))
    ba_dashboards = list(set(ba_dashboards))
    ba_charts = list(set(ba_charts))
    ba_datasets_uuid = list(set(ba_datasets_uuid))
    common_ba_dataset_names.extend(ba_datasets_names)

    # список идишников на удаление
    delete_dataset = [entity['id'] for entity in new_datasets if entity["table_name"] in ba_datasets_names]
    delete_dashboards = [entity['id'] for entity in new_dashboards if entity["dashboard_title"] in ba_dashboards]
    delete_charts = [entity['id'] for entity in new_charts if entity["slice_name"] in ba_charts]

    ba_dataset_from_zip=[ba_full_datasets[entity]['id'] for entity in ba_datasets_uuid if entity in ba_full_datasets]# по uuid найдем Id датасетов  из zip файлов

    ba_dataset_id_to_delete =[full_ba_reports_ids[entity]['dataset_id'] for entity in full_ba_reports_ids if full_ba_reports_ids[entity]['dataset_id'] in ba_dataset_from_zip] # найдем id датасетов у которые точно есть репорты из ZIP файдла

    name_dataset_to_delete_report =[ba_full_datasets[entity]['name'] for entity in ba_full_datasets if ba_full_datasets[entity]['id'] in  ba_dataset_id_to_delete] #получим список имен датасетов у которых есть отчеты

    dataset_with_reports_id = [entity['id'] for entity in new_datasets if entity['table_name'] in name_dataset_to_delete_report] # по именам найдем id датасетов у заказчика у который могут быть отчеты у

    reports_to_delete=[entity['id'] for entity in new_reports if entity['dataset_id'] in dataset_with_reports_id] #по id датасетов взаказчика найдетм id репортов которые надо дропнуть

    # дропаем
    local_logger.info(f'дропаем чарты  {delete_charts}')
    [del_charts(access_token, entity, superset_domain)  for entity in delete_charts]
    local_logger.info(f'дропаем датасеты  {delete_dataset}')
    [del_dataset(access_token, entity, superset_domain)  for entity in delete_dataset]
    local_logger.info(f'дропаем дашборды  {delete_dashboards}')
    [del_dashboard(access_token, entity, superset_domain)  for entity in delete_dashboards]

    local_logger.info(f'дропаем репорты  {reports_to_delete}')
    [del_report(access_token, entity, superset_domain)  for entity in reports_to_delete]

    #экспорт
    database_name = None
    for entity in client_database:
        db = entity['database_name']
        if db == database_from_zip:
            database_name = entity['database_name']
            uri = entity['sqlalchemy_uri']
            uuid = entity['uuid']
            break
    if not database_name:
        local_logger.error(f"база данных не найдена {database_from_zip}")
        continue

    if len(params['databases'])!=1:
        print(f"dashboard имеет не одну БД {len(params)}")
        exit(1)
    zip_corrector(sqlalchemy_uri= uri, database_uuid=uuid, database_name=database_name, output_dir=output_directory, zip_file=one_file)
    local_logger.info(f'импортим сущность  {one_file}')
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
                local_logger.info(f'импортим репорт {new_id}  {output_file}')
                try:
                    import_report_template(access_token, new_id, output_file, desc, superset_domain)
                except Exception as e:
                    local_logger.error(f"{str(e)}")
exit(1)
#---------------------------------------------------------------------------------------------------------------------
