#python 3.5

import sys
import http.client
import json
import re
import time

target_ip = '172.16.202.201'
target_port = 69

path_portal = '/cgi-bin/srun_portal'
path_info = '/cgi-bin/rad_user_info'

usr_name = ''
pwd = ''
# TODO: read username from file

profiles = {
    'accounts': [],
    'accounts_sel' : 0,

}

def add_accuont(usr_name, pwd):
    account = {'username': usr_name, 'pwd': pwd}
    profiles['accounts'].append(account)
    profiles['accounts_sel'] = len(profiles['accounts'])-1


profile_file_name = 'profiles.json'

try:
    f_prf = open(profile_file_name, 'r+')
    print('loading profiles...')
    try:
        profiles = json.loads(f_prf.read())
        usr_name = profiles['accounts'][profiles['accounts_sel']]['username']
        pwd = profiles['accounts'][profiles['accounts_sel']]['pwd']
    except Exception as e:
        print('an error occurs when reading profiles file:', e)
    
except Exception as e:
    print('no profiles file')
    while len(usr_name) == 0:
        usr_name = input('please input your username:\n')
    while len(pwd) == 0:
        pwd = input('please input your password:\n')
    add_accuont(usr_name, pwd)

    try:
        f_prf = open(profile_file_name, 'w')
        f_prf.write(json.dumps(profiles, indent=4))
        f_prf.close()
    except Exception as e:
        print('an error occurs when writing profiles file:', e)




def check_info():
    conn = http.client.HTTPConnection(target_ip, target_port)
    # connect
    conn.request('GET', path_info)
    resp = conn.getresponse()
    # response
    response_text = str(resp.read(), 'utf-8')
    conn.close()
    # return response_text

    if response_text == 'not_online':
        # not online
        return False
    else:
        # parse response
        splited_text = response_text.split(',')
        online_info = {
            'username': splited_text[0],
            'login_timestamp': splited_text[1],
            # time stamp is in second
            'data_usage_curr_login': splited_text[3],
            'total_data_usage': splited_text[6],
            'ip': splited_text[8],
            'balance': splited_text[11],
        }
        return online_info


def login(usr_name, pwd):
    headers_login = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    cont_login = 'username={}&password={}&ac_id=1&action=login&type=1&n=100'
    req_body = cont_login.format(usr_name, pwd)

    conn = http.client.HTTPConnection(target_ip, target_port)
    conn.request('POST', path_portal, req_body, headers_login)
    resp = conn.getresponse()
    response_text = str(resp.read(), 'utf-8')
    conn.close()
    return response_text

def logout(usr_name):
    headers_logout = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    cont_logout = 'action=logout&ac_id=1&username={}&type=2'
    req_body = cont_logout.format(usr_name)

    conn = http.client.HTTPConnection(target_ip, target_port)
    conn.request('POST', path_portal, req_body, headers_logout)
    resp = conn.getresponse()
    response_text = str(resp.read(), 'utf-8')
    conn.close()
    return response_text

def data_unit(in_byte):
    if isinstance(in_byte, str):
        in_byte = int(in_byte)
    if in_byte < 1024:
        converted = '{} byte(s)'.format(in_byte)
    elif in_byte < 1024 * 1024:
        converted = '{} KiB'.format('%.2f' % (in_byte / 1024))
    elif in_byte < 1024 * 1024 * 1024:
        converted = '{} MiB'.format('%.2f' % (in_byte / 1024 / 1024))
    else:
        converted = '{} GiB'.format('%.2f' % (in_byte / 1024 / 1024 / 1024))
    return converted

def ts_to_time(ts):
    # timestamp to formatted time
    if isinstance(ts, str):
        ts = int(ts)
    t = time.localtime(ts)
    t_formated = time.strftime("%Y-%m-%d %H:%M:%S", t)
    return t_formated

while True:

    online_info = check_info()
    if online_info:
        print()
        print('now online')
        print('username:', online_info['username'])
        print('login time:', ts_to_time(online_info['login_timestamp']))
        print('data usage:', data_unit(online_info['data_usage_curr_login']))
        print('total data usage:', data_unit(online_info['total_data_usage']))
        print('ip:', online_info['ip'])
        print('balance', '%.2f' % float(online_info['balance']))
        print()
    else:
        print()
        print('not online')
        print()

    op = input('input "login" to log in, "logout" to log out, "e" to exit program, others to check infomation:\n')

    
    if op in ('e', 'q', 'exit', 'quit'):
        print('exit...')
        break

    elif op in ('login', 'log in', 'log on'):
        if online_info:
            print('you have already logged in')
        else:
            print('loging in...')

            response_text = login(usr_name, pwd)
            print(response_text)
            
            if response_text.startswith('login_ok'):
                print('succeeded logging in')
            else:
                m = re.search('\#((.*)\:(.*))', response_text)
                if m:
                    print('Error:', m.groups()[0])
                else:
                    print('Unknown error')
    elif op in ('logout', 'log out'):
        if online_info:
            print('logging out...')

            response_text = logout(usr_name)
            if response_text.startswith('logout_ok'):
                print('succeeded logging out')
            else:
                print('failing logging out')
        else:
            print('not online')
    else:
        pass
