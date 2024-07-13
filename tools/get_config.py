from configparser import ConfigParser


config = ConfigParser()
config.read(r".\config\config.ini")

def get_es_config():
   es_user=config['elastic']['username']
   es_pass=config['elastic']['password']
   es_host_1=config['elastic']['host_1']
   es_ca_certs=config['elastic']['ca_certs']

   details={'es_user':es_user,
            'es_pass':es_pass,
            'es_host_1':es_host_1,
            'es_ca_certs':es_ca_certs}
   return details
