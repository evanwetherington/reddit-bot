import random
import time
import json
import mysql.connector
from threading import Lock


sql_lock: Lock = Lock()


def get_db_connection() -> mysql.connector:
    try:
        file = open('credentials.json')
        credentials = json.load(file)
        return mysql.connector.connect(
            host=credentials["dbhost"],
            user=credentials["dbuser"],
            password=credentials["dbpassword"],
            database="reddit",
            charset='utf8mb4')
    except FileNotFoundError as fnfe:
        print('Could not find user credentials file.')
        raise fnfe
    except Exception as e:
        print("Error Loading Database Credentials.")
        raise e


def get_oldest_ids(table, rows):
    result = exec_sql_query("SELECT id FROM "+table+" order by updated_dttm asc limit "+str(rows)+";")
    ids = [id[0] for id in result]
    return ids


def exec_sql_query(sql, values=None, run_many=False):
    mydb: mysql.connector.connection = None
    for retries in range(3):
        try:
            mydb = get_db_connection()
            cursor = mydb.cursor()
            if run_many:
                cursor.executemany(sql, values)
            else:
                cursor.execute(sql, values)
            rows = cursor.fetchall()
            mydb.commit()
            return rows
        except Exception as e:
            print("***Error executing sql statement.\r\n"+ str(e)) + "\r\nSQL: " + sql
            for v in values:
                print(v[10])
            time.sleep(random.random() + retries)
        finally:
            if mydb:
                mydb.disconnect()


def exec_sql(sql, values=None, run_many=False):
    mydb: mysql.connector.connection = None
    for retries in range(3):
        try:
            mydb = get_db_connection()
            cursor = mydb.cursor()
            if run_many:
                cursor.executemany(sql, values)
            else:
                cursor.execute(sql, values)
            mydb.commit()
        except Exception as e:
            for v in values:
                print(v[10])
            print("***Error executing sql statement.\r\n" + str(e))
            time.sleep(random.random() + retries)
        finally:
            if mydb:
                mydb.disconnect()


def insert_with_replacements(table, column_names: str, values):
    txt = 'insert into ' + table + \
          ' ('+ column_names + ') ' + \
          'values (' + "%s" + ",%s"*(len(column_names.split(','))-1) + ') ' \
          'ON duplicate key update '
    for name in column_names.split(','):
        txt = txt + name + '= values(' + name + "), "
    txt = txt[:-2]
    txt = txt + ';'
    exec_sql(txt, values, True)
