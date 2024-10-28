from elasticsearch import Elasticsearch
import psycopg2
from . import get_config

def es_connect():
    es = get_config.es_config()

    es_user = es['es_user']
    es_pass = es['es_pass']
    es_host_1 = es['es_host_1']
    es_ca_certs = es['es_ca_certs']
    client = Elasticsearch(
        hosts=es_host_1,
        ca_certs=es_ca_certs,
        basic_auth=(es_user, es_pass)
    )
    return client

def db_connect():
    db = get_config.db_config()

    db_name = db['db_name']
    db_user = db['db_user']
    db_pass = db['db_password']
    db_host = db['db_host']
    db_port = db['db_port']

    connection = psycopg2.connect(database = db_name, user = db_user, password = db_pass, host = db_host, port = db_port)
    
    return connection


# cursor = db_connect()
# cursor.execute("SELECT * FROM bills;")
# record = cursor.fetchall()

# for row in record:
#     print(row)