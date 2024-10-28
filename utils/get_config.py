from configparser import ConfigParser
import os

config = ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
config.read(config_file_path)

def es_config():
   es_user = config['elastic']['username']
   es_pass = config['elastic']['password']
   es_host_1 = config['elastic']['host_1']
   es_ca_certs = config['elastic']['ca_certs']

   details={'es_user':es_user,
            'es_pass':es_pass,
            'es_host_1':es_host_1,
            'es_ca_certs':es_ca_certs}
   return details

def db_config():
   db_name = config['database']['database_name']
   db_user = config['database']['user']
   db_password = config['database']['password']
   db_host = config['database']['host']
   db_port = config['database']['port']

   details={'db_name' : db_name,
            'db_user' : db_user,
            'db_password' : db_password,
            'db_host' : db_host,
            'db_port' : db_port
            }
   return details
