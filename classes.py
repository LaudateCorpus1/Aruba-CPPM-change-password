"""Class defition file"""
from configparser import ConfigParser
import os
import sys

class cppm_connect:
    """ This class defines parameters to connect to the Clearpass 
    and some additional parameters
    Args:
            params (str): Parameters files to be read:
                params_1.cfg - main parameters file
                params_2.cfg - passwords file ( TODO: passwords have to be encrypted)
    """
    def __init__(self):
       
        self.params = os.path.join \
        (os.path.dirname(__file__), "config/params_1.cfg")
        self.config = ConfigParser()
        self.config.read(self.params)
        self.clearpass_fqdn = self.config.get('ClearPass', 'clearpass_fqdn')
        self.oauth_grant_type = self.config.get('OAuth2', 'grant_type')
        self.oauth_client_id_rw = self.config.get('OAuth2', 'client_id_rw')
        self.oauth_client_id_ro = self.config.get('OAuth2', 'client_id_ro')
        self.oauth_username = self.config.get('OAuth2', 'username')
        self.db_username = self.config.get('DB', 'username')
        self.days_to_passw_exp = self.config.get('Misc', 'days_to_passw_exp')
        #self.oauth_client_secret = self.config.get('OAuth2', 'client_secret')

        self.params = os.path.join \
        (os.path.dirname(__file__), "config/params_2.cfg")
        self.config = ConfigParser()
        self.config.read(self.params)
        self.oauth_password = self.config.get('OAuth2', 'password')
        self.db_password = self.config.get('DB', 'password')
#        self.username = None is not used yet
#        self.password = None
        self.status_code = 0
        self.user_type = 'Undefined'
