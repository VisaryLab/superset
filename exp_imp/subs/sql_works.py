import subprocess
import os
from subs.config import *

# Database connection details
def pg_backup(tablename,output_dir):
    pg = export_pg
    DB_HOST = pg['host']
    DB_PORT = pg['port']
    DB_NAME = pg['database']
    DB_USER = pg['user']
    TABLE_NAME = pg['host']
    BACKUP_FILE = pg['host']
    SCHEME = pg['scheme']
    os.environ["PGPASSWORD"] = pg["PASSWORD"]
#pg_dump -h 192.168.1.109 -U datahub  -p 5432 -d datahub  -t gar.adm -f adm.sql


    # Construct the pg_dump command
    command = [
        "pg_dump",
        "-h", DB_HOST,
        "-U", DB_USER,
        "-d", DB_NAME,
        "-p", str(DB_PORT),
        "-t", SCHEME+'.'+"adm",  # Specify the table to backup
        "-f", os.path.join(output_dir, tablename)
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Table '{TABLE_NAME}' backed up successfully to '{BACKUP_FILE}'")
    except subprocess.CalledProcessError as e:
        print(f"Error during backup: {e}")
        print(e.stderr)
    finally:
        # Unset the password environment variable
        del os.environ["PGPASSWORD"]


def restore(tablename,output_dir):
    # Database connection details
    pg = export_pg
    DB_HOST = pg['host']
    DB_PORT = pg['port']
    DB_NAME = pg['database']
    DB_USER = pg['user']
    TABLE_NAME = pg['host']
    BACKUP_FILE = pg['host']
    os.environ["PGPASSWORD"] = pg["PASSWORD"]
    # psql -h 192.168.1.109 -U datahub  -p 5432 -d datahub -f adm.sql

    command = [
        "psql",
        "-h", DB_HOST,
        "-U", DB_USER,
        "-p", str(DB_PORT),
        "-d", DB_NAME,
        "-f", os.path.join(output_dir, tablename)
    ]
    try:
        subprocess.run(command, check=True)
        print(f"Table '{TABLE_NAME}' restored successfully from '{BACKUP_FILE}'")
    except subprocess.CalledProcessError as e:
        print(f"Error during backup: {e}")
        print(e.stderr)
    finally:
        del os.environ["PGPASSWORD"]

def drop(tablename):
    # Database connection details
    pg = export_pg
    DB_HOST = pg['host']
    DB_PORT = pg['port']
    DB_NAME = pg['database']
    DB_USER = pg['user']
    TABLE_NAME = pg['host']
    BACKUP_FILE = pg['host']
    os.environ["PGPASSWORD"] = pg["PASSWORD"]

    #  psql -h 192.168.1.109 -U datahub  -p 5432 -d datahub -c "drop table gar.adm;"

    command = [
        "psql",
        "-h", DB_HOST,
        "-U", DB_USER,
        "-p", str(DB_PORT),
        "-d", DB_NAME,
        "-c",  f'"drop table {tablename};"' #со схемой!!!   public.table типа
    ]
    try:
        subprocess.run(command, check=True)
        print(f"Table '{TABLE_NAME}' restored successfully from '{BACKUP_FILE}'")
    except subprocess.CalledProcessError as e:
        print(f"Error during backup: {e}")
        print(e.stderr)
    finally:
        del os.environ["PGPASSWORD"]









