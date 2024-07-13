import get_config
from elasticsearch import Elasticsearch

con = get_config.get_es_config()


def es_conn():
    es_user=con['es_user']
    es_pass=con['es_pass']
    es_host_1=con['es_host_1']
    es_ca_certs=con['es_ca_certs']
    client = Elasticsearch(
        hosts=es_host_1,
        ca_certs=es_ca_certs,
        basic_auth=(es_user, es_pass)
    )
    # print(client.info())
    return client

def create_index(conn,name):
    try: 
        res = conn.indices.create(index=f"{name}")
        return 201 #this is for created
    except Exception as e: 
        return 409 #this is for conflic index already exists