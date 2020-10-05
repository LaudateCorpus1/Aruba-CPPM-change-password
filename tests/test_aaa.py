#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests

@author: semenov-ay
"""
# Imports
import os
import sys
import psycopg2
import pytest
from configparser import ConfigParser
from classes import Cppm_Connect
from common_functions import get_access_token
from aaa_change_password import exp_days_f

sys.path.append("..")

# Parameters to check in test_file1_parameters function
config_options = [['ClearPass', 'clearpass_fqdn'], ['OAuth2', 'grant_type'],
                  ['OAuth2', 'client_id_rw'], ['OAuth2', 'client_id_ro'],
                  ['OAuth2', 'username'], ['DB', 'username'],
                  ['Misc', 'days_to_passw_exp']]


# TODO
# 'Please check Cleapass FQDN or IP in the Clearpass section of the params file'
# 'Please check grant_type definition in the OAuth2 section of the params file'
# 'Please check client_id_rw definition in the OAuth2 section of the params file'
# 'Please check client_id_ro definition in the OAuth2 section of the params file'
# 'Please check username definition in the OAuth2 section of the params file'
# 'Please check username definition in the DB section of the params file'
# 'Please check days_to_passw_exp definition in the Misc section of the params file'


@pytest.mark.parametrize("section,option", config_options)
def test_file1_parameters(section, option):
    """
    Check parameters in the main file 
    """
    params = os.path.join(os.path.dirname(__file__), "../config/params_1.cfg")
    config = ConfigParser()
    config.read(params)
    assert config.has_option(section, option) is True
    return


# Parameters to check in test_file2_parameters function
config_options = [['OAuth2', 'password'], ['DB', 'password']]


# TODO
# 'Please check password definition in the OAuth2 section of the params2 file'
# 'Please check password definition in the DB section of the params file'


@pytest.mark.parametrize("section,option", config_options)
def test_file2_parameters(section, option):
    """
    Check parameters in the password file
    """
    params = os.path.join(os.path.dirname(__file__), "../config/params_2.cfg")
    config = ConfigParser()
    config.read(params)
    assert config.has_option(section, option) is True
    return


# Define class from classes file
connect_class = Cppm_Connect()


def cppm_ping():
    """
    Clearpass  Ping publisher function
    """
    cppm_response = os.system(f'ping -c 3 {connect_class.clearpass_fqdn}')
    return cppm_response


# Call Clearpass ping publisher function
ping_response = cppm_ping()


def test_cppm_ping():
    """
    Ping test publisher's IP 
    """
    assert ping_response == 0, 'Please check Clearpass publisher availability'
    return


# Сценариев пока нет
scenarios_to_check_api = [
    (connect_class.db_username, connect_class.db_password),
    (connect_class.db_username, '123456'),
    ('db_username', connect_class.db_password)]


# SKIP TEST if Publisher is not pinged


@pytest.mark.skipif(ping_response != 0, reason="cannot ping CPPM")
# @pytest.mark.parametrize("chk_name,chk_pass,api_method",
# scenarios_to_check_api, ids =["right_pass", "wrong_pass","wrong_name"])
def test_clearpass_api_connection():
    """
    Clearpass API connectivity tests
    """
    token_response, status_code = get_access_token(connect_class, 'None',
                                                   'None', 'nologin')
    assert status_code == 200
    return


scenarios_to_check_db = [
    (connect_class.db_username, connect_class.db_password, True),
    (connect_class.db_username, 'wrong_db_pass', False),
    ('wrong_db_username', connect_class.db_password, False)]


# SKIP TEST if Publisher is not pinged
@pytest.mark.skipif(ping_response != 0, reason="cannot ping CPPM")
@pytest.mark.parametrize("chk_name,chk_pass,chk_flag", scenarios_to_check_db,
                         ids=["right_pass",
                              "wrong_pass", "wrong_name"])
def test_clearpass_postgres_conn(chk_name, chk_pass, chk_flag):
    """
    Clearpass Postgress DB connectivity checking (Login/password)
    """
    if chk_flag:
        conn = psycopg2.connect(f"dbname='tipsdb' user={chk_name}"
                                f" host={connect_class.clearpass_fqdn}"
                                f" password={chk_pass} connect_timeout=2"
                                "sslmode=require")
        assert conn.status == 1
        conn.close()
    else:
        with pytest.raises(Exception) as sql_conn_error:
            conn = psycopg2.connect(f"dbname='tipsdb' user={chk_name}"
                                    f" host={connect_class.clearpass_fqdn}"
                                    f" password={chk_pass} connect_timeout=2"
                                    "sslmode=require")
        assert "no pg_hba.conf" in str(sql_conn_error.value)
    return


# SKIP TEST if Publisher is not pinged
@pytest.mark.skipif(ping_response != 0, reason="cannot ping CPPM")
def test_exp_days_f():
    """
    Testing expiration password function from main app file
    """
    user = 'test_pass_expiry'
    exp_days_tuple = exp_days_f(connect_class, user)
    assert exp_days_tuple[0] <= int(connect_class.days_to_passw_exp)
    assert exp_days_tuple[1] is False
    # Right assertion for expired user
    #   assert exp_days_tuple[0] >= int(connect_class.days_to_passw_exp)
    #   assert exp_days_tuple[1] == True
    return
