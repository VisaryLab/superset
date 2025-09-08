master_db = ['webapi_db', 'audit_db']
output_directory = './output'
tmp_directory = './tmp_output'

# суперсет откуда тащим
ba_superset_domain = "http://172.17.103.29:8088"
ba_connect_params = {
    "username":"admin",
    "password":"admin",
    "provider":"db",
    "refresh":True
}

#суперсет куда тащим
superset_domain = "http://192.168.1.109:8088"
connect_params = {
    "username":"123456",
    "password":"123456",
    "provider":"db",
    "refresh":True
}

#webapi_db у заказчика
client_database = [
        {'database_name': 'webapi_db', 'sqlalchemy_uri': 'postgresql+psycopg2://visary:123456@192.168.1.109:5432/webapi_db', 'uuid': '7c721b9e-e343-4e06-9b51-333385e1675d'},
        {'database_name': 'audit_db', 'sqlalchemy_uri': 'postgresql+psycopg2://visary:123456@192.168.1.109:5432/audit_db', 'uuid': '7c721b9e-e343-4e06-9b51-333385e1675e'}
                  ]
client_sqlalchemy_uri = 'postgresql+psycopg2://visary:%s@%s:%s/%s'
client_sqlalchemy_engine = 'postgresql'


# ниже парамсы могут окоазаться лишними и исчезнуть
import_pg = {"user":'admin',
             "password":'admin',
             "host":'192.168.1.109',
             "port":5432,
             "database":'superset',
             "scheme":'superset'
             }

export_pg = {"user":'visary',
             "password":'123456',
             "host":'192.168.1.109',
             "port":5432,
             "database":'superset',
             "scheme":'superset'
             }