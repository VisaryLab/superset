#сохраняем смущности SS в виде zip файлов на диске
from subs.datasets import *
from subs.dashboards import *
from subs.auth import *
from subs.reports import *
from subs.database import *
from subs.charts import *
import json

output_directory = './output'
access_token, refresh_token = get_tokens()
for a in  get_databases(access_token, output_directory, ba_superset_domain):
    b = json.loads(a)
    id = b['id']
    name = b['database_name']
    export_database(access_token, id, name, output_directory, ba_superset_domain)

for a in  get_datasets(access_token, output_directory, ba_superset_domain):
    b = json.loads(a)
    id = b['id']
    name = b['table_name']
    export_dataset(access_token, id, name, output_directory, ba_superset_domain)

for a in get_dashboards(access_token, output_directory, ba_superset_domain):
    b = json.loads(a)
    id = b['id']
    name = b['dashboard_title']
    export_dashbord(access_token, id, name, output_directory, ba_superset_domain)

#for a in  get_css_templates(access_token, output_directory, ba_superset_domain):
#    b = json.loads(a)
#    id = b['id']
#    name = b['template_name']
#    export_css_template(access_token, id, name, output_directory, ba_superset_domain)

for a in  get_report_templates(access_token, output_directory, ba_superset_domain):
    b = json.loads(a)
    id = b['id']
    name = b['name']
    export_report_template(access_token, id, name, output_directory, ba_superset_domain)

#for a in  get_charts(access_token, output_directory, ba_superset_domain):
#    b = json.loads(a)
#    id = b['id']
#    name = b['slice_name']
#    export_chart(access_token, id, name, output_directory, ba_superset_domain)

exit(1)


