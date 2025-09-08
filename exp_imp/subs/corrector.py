import tempfile
import zipfile
import os
import yaml as yam_yam

def search_in_strs(in_str,key):
    ttt = None
    for num, one_str in enumerate(in_str):
        if one_str.startswith(key):
            tmp = one_str.split(': ')
            ttt = tmp[1].strip()
            break
    return ttt


def get_db_params_zip(output_dir:str, zip_file:str):
    params ={}
    params["datasets"]=[]
    params["databases"] = []
    params["dashboards"] = []
    params["charts"] = []

    zf = zipfile.ZipFile(os.path.join(output_dir, zip_file))
    sub_main = ''
    with tempfile.TemporaryDirectory() as temp_dir:
        zf.extractall(temp_dir)
        for dirpath, dirnames, filenames in os.walk(temp_dir):
            if dirnames and sub_main=='':
                sub_main = dirnames[0]
            if 'databases' in dirpath:
                if filenames:
                    for one_file in filenames:
                        fullname = os.path.join(dirpath, one_file)
                        #print(fullname)
                        with open(fullname, 'r') as ya:
                            yaml = ya.readlines()
                            ya_dict = yam_yam.safe_load(''.join(yaml))
                            uuid= ya_dict.get('uuid')
                            sqlalchemy_uri= ya_dict.get('sqlalchemy_uri')
                            database_name = ya_dict.get('database_name')
                            params["databases"].append({'uuid':uuid, 'sqlalchemy_uri':sqlalchemy_uri, "database_name":database_name})

            elif 'datasets' in dirpath:
                if filenames:
                    for one_file in filenames:
                        fullname = os.path.join(dirpath, one_file)
                        #print(fullname)
                        with open(fullname, 'r') as ya:
                            yaml = ya.readlines()
                            ya_dict = yam_yam.safe_load(''.join(yaml))
                            table_name= ya_dict.get('table_name')
                            id= ya_dict.get('id')
                            uuid= ya_dict.get( 'uuid')
                            params["datasets"].append({'uuid':uuid, 'table_name':table_name, "id":id })

            elif 'dashboards' in dirpath:
                if filenames:
                    for one_file in filenames:
                        fullname = os.path.join(dirpath, one_file)
                        #print(fullname)
                        with open(fullname, 'r') as ya:
                            yaml = ya.readlines()
                            ya_dict = yam_yam.safe_load(''.join(yaml))
                            uuid= ya_dict.get( 'uuid')
                            name= ya_dict.get( 'name')
                            dashboard_title= ya_dict.get( 'dashboard_title').encode('utf-8').decode('utf-8')
                            params["dashboards"].append({'uuid':uuid, "name":name, 'dashboard_title':dashboard_title})

            elif 'charts' in dirpath:
                if filenames:
                    for one_file in filenames:
                        fullname = os.path.join(dirpath, one_file)
                        #print(fullname)
                        with open(fullname, 'r') as ya:
                            yaml = ya.readlines()
                            ya_dict = yam_yam.safe_load(''.join(yaml))
                            uuid= ya_dict.get( 'uuid')
                            slice_name= ya_dict.get( 'slice_name')
                            params["charts"].append({'uuid':uuid, 'slice_name':slice_name})
    return params


def replace_in_strs(in_str,key, value):
    ttt = None
    for num, one_str in enumerate(in_str):
        if one_str.startswith(key):
            tmp = one_str.split(': ')
            ttt = tmp[0]+': '+value+'\n'
            break
    if ttt:
        in_str[num] = ttt
    return

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))


def zip_corrector(sqlalchemy_uri, database_uuid, database_name, output_dir, zip_file):
    zf = zipfile.ZipFile(os.path.join(output_dir, zip_file))
    sub_main = ''
    with tempfile.TemporaryDirectory() as temp_dir:
        zf.extractall(temp_dir)
        for dirpath, dirnames, filenames in os.walk(temp_dir):
           # print(f'Directory: {dirpath}')
           # print(f'Subdirectories: {dirnames}')
           # print(f'Files: {filenames}')
           # print('--------------------------------')
            if dirnames and sub_main=='':
                sub_main = dirnames[0]
            if 'databases' in dirpath:
                if filenames:
                    for one_file in filenames:
                        fullname = os.path.join(dirpath, one_file)
                        print(fullname)
                        with open(fullname, 'r') as ya:
                            yaml = ya.readlines()
                            if database_name ==search_in_strs(yaml, 'database_name'):
                                replace_in_strs(yaml, 'uuid', database_uuid)
                                replace_in_strs(yaml, 'sqlalchemy_uri', sqlalchemy_uri)
                        with open(fullname, 'w') as ya:
                            print(f'переписан файл {fullname}')
                            ya.writelines(yaml)
            if 'datasets' in dirpath:
                if filenames:
                    for one_file in filenames:
                        fullname = os.path.join(dirpath, one_file)
                        print(fullname)
                        with open(fullname, 'r') as ya:
                            yaml = ya.readlines()
                            replace_in_strs(yaml, 'database_uuid', database_uuid)
                        with open(fullname, 'w') as ya:
                            print(f'переписан файл {fullname}')
                            ya.writelines(yaml)
        #name, ext = os.path.splitext(zip_file)
        #name = name +'_patched'+ext
        with zipfile.ZipFile(os.path.join(output_dir, zip_file), 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipdir(os.path.join(temp_dir, sub_main), zipf)

