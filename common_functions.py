"""
Common functions for change password
and email (future use) notification applications
"""
# Imports
import json
import requests
import psycopg2


def get_access_token(cppm_class, oauth_username, oauth_password,
                     get_access_type):
    """
    Function to get Clearpass OAuth 2.0 access token from CPPM

    Args:
        cppm_class: cppm_connect class from classes.py
        oauth_username: username which connects to API
        oauth_password: oauth_username password
        get_access_type: Access type 'login' used for local user access,
                         other - for internal user

    Returns:
       json_response:  Clearpass API Oauth access token
       (in JSON response message)
       if authentication successful or error in JSON format
       get_token.status_code: Status code for the Request call

        HTTP Status Code      Reason
           200 	                OK
           400 	                Bad Request
           406 	                Not Acceptable
           415                  Unsupported Media Type
    """
    # Define connection parameters
    url = f'https://{cppm_class.clearpass_fqdn}/api/oauth'
    headers = {'Content-Type': 'application/json'}
    get_token = None

    if cppm_class.oauth_grant_type == "password":
        if get_access_type == 'login':
            payload = {'grant_type': cppm_class.oauth_grant_type,
                       'username': oauth_username,
                       'password': oauth_password,
                       'client_id': cppm_class.oauth_client_id_ro}
        else:
            payload = {'grant_type': cppm_class.oauth_grant_type,
                       'username': cppm_class.oauth_username,
                       'password': cppm_class.oauth_password,
                       'client_id': cppm_class.oauth_client_id_ro}
        try:
            get_token = requests.post(url, headers=headers, json=payload,
                                      verify=False, timeout=4)
            #               print (oauth_username , get_token)
            get_token.raise_for_status()
        except requests.exceptions.Timeout:
            print('timeout')
        #                   return None
        except Exception as get_access_exception:
            print('G_A_T Exception', get_access_exception)

        json_response = json.loads(get_token.text)
        print(json_response, get_token.status_code)
        return json_response, get_token.status_code


def change_password(cppm_class, username, newpassword):
    """
    Change Password function through API (uses get_access_token function)

    Args:
        cppm_class: cppm_connect class from classes.py
        username: Logged username
        newpassword: new password

    Returns:
        patch_user_status: default is None, if change password unsuccessful
                                            than return the reason
        patch_user_code: Status code for the Request call

        HTTP Status Code 	Reason
                200 	           OK
                204 	           No Content
                304                Not Modified
                401 	           Unauthorized
                403 	           Forbidden
                404 	           Not Found
                406 	           Not Acceptable
                415 	           Unsupported Media Type
                422 	           Unprocessable Entity
    """
    # Define patch_user_status
    patch_user_status = None
    oauth_username = None
    oauth_password = None
    get_access_type = "change_password"
    # Get Bearer and Access Token for change
    try:
        token_response, status_code = get_access_token(cppm_class,
                                                       oauth_username,
                                                       oauth_password,
                                                       get_access_type)
        access_token = token_response['access_token']
        token_type = token_response['token_type']
        if  cppm_class.user_type != 'Admin':
            url = f'https://{cppm_class.clearpass_fqdn}/api/local-user/user-id/{username}'
        else:
            url = f'https://{cppm_class.clearpass_fqdn}/api/admin-user/user-id/{username}'
        headers = {'Accept': 'application/json',
                   "Authorization": f"{token_type} {access_token}"}
        payload = {'password': newpassword}
        patch_user = requests.patch(url, headers=headers, json=payload,
                                    verify=False, timeout=4)
        patch_user_code = patch_user.status_code
        #    print('F patch_user_code', patch_user_code)
        if patch_user_code != 200:
            patch_user_status = (json.loads(patch_user.text)['detail'])
            print('F patch_user_status', patch_user_status)
        return patch_user_status, patch_user_code
    except Exception as change_pwd_exception:
        print('CP Exception', change_pwd_exception)


def pg_sql(pg_select, cppm_class, username):
    """
    Clearpass Postgress connection and read function

    Args:
        pg_select: defines which DB connect to (only LocalDb is used)
        cppm_class: cppm_connect class from classes.py
        username: Localuser DB username

    Returns:
       data: string or strings (will be used in future) from tipsDB
           Columns from DB:
               user_id
               password_updated_at
               attributes
               change_pwd_next_login
    """
    # Define Postgress connection parameters
    conn = psycopg2.connect(f"dbname='tipsdb' user={cppm_class.db_username}"
                            f" host={cppm_class.clearpass_fqdn}"
                            f" password={cppm_class.db_password}"
                            f" sslmode=require")
    # Define SELECT from DB
    if pg_select == 'user':
        # Select for particular user
        sql = f"SELECT user_id, password_updated_at, attributes, change_pwd_next_login \
        FROM public.tips_auth_local_users WHERE user_id LIKE \'{username}\'"
    else:
        # Select for all user
        sql = "SELECT user_id, password_updated_at, attributes \
        FROM public.tips_auth_local_users"
    try:
        cur = conn.cursor()
        cur.execute(sql)
    except psycopg2.Error as err:
        print(f"Query error: {err}")
    # Get row for particular user from table "tips_auth_local_users"
    if pg_select == 'user':
        # Get data for for particular user
        data = cur.fetchone()
    else:
        # Get data for all users
        data = cur.fetchall()
    # close Postgress DB connection
    cur.close()
    conn.close()
    return data


def check_user_status(cppm_class, username):
    """
    Check user status (admin or not) function through API (uses get_access_token function)

    Args:
        cppm_class: cppm_connect class from classes.py
        username:  Username logged in

    Returns:
        check_status_code: Status code for the Request call

        HTTP Status Code 	Reason
                200 	           OK
                401 	           Unauthorized
                403 	           Forbidden
                404 	           Not Found
                406 	           Not Acceptable
                415 	           Unsupported Media Type
    """
    oauth_username = None
    oauth_password = None
    get_access_type = "check_user_status"
    # Get Bearer and Access Token for check
    try:
        token_response, status_code = get_access_token(cppm_class,
                                                       oauth_username,
                                                       oauth_password,
                                                       get_access_type)
        access_token = token_response['access_token']
        token_type = token_response['token_type']
    # Check if user exists in the Admin DB   
        url = f'https://{cppm_class.clearpass_fqdn}/api/admin-user/user-id/{username}'
        headers = {'Accept': 'application/json',
                   "Authorization": f"{token_type} {access_token}"}
        payload = {}
        check_user = requests.get(url, headers=headers, json=payload,
                                    verify=False, timeout=4)
        check_status_code = check_user.status_code
        # print ('STATUS CODE',check_status_code)
        return check_status_code
    except Exception as check_user_exception:
        print('CP Exception', check_user_exception)