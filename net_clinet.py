#python 3.5
# -*- coding: utf-8 -*-

import sys
import http.client
import json
import re
import time

target_ip = '172.16.202.201'
target_port = 69

path_portal = '/cgi-bin/srun_portal'
path_info = '/cgi-bin/rad_user_info'

username = ''
pwd = ''

profiles = {
    'accounts': [],
    'accounts_sel' : 0,

}

def require_account():
    username = ''
    pwd = ''
    while len(username) == 0:
        username = input('please input your username:\n>>')
    while len(pwd) == 0:
        pwd = input('please input your password:\n>>')
    return (username, pwd)

def add_accuont(username, pwd):
    account = {'username': username, 'pwd': pwd}
    profiles['accounts'].append(account)

def set_selected(num):
    if len(profiles['accounts']) > num:
        profiles['accounts_sel'] = num
    else:
        print('set_selected: num out of range')


profile_file_name = 'profiles.json'

def save_profile():
    try:
        f_prf = open(profile_file_name, 'w')
        f_prf.write(json.dumps(profiles, indent=4))
        f_prf.close()
    except Exception as e:
        print('an error occurs when writing profiles file:', e)




try:
    f_prf = open(profile_file_name, 'r+')
    print('loading profiles...')
    try:
        profiles = json.loads(f_prf.read())
        selected = profiles['accounts_sel']
        if len(profiles['accounts']) < selected + 1:
            raise 'selected accounts not exist'
        username = profiles['accounts'][selected]['username']
        pwd = profiles['accounts'][selected]['pwd']
    except Exception as e:
        print('an error occurs when reading profiles file:', e)
    
except Exception as e:
    print('no profiles file')
    (username, pwd) = require_account()
    add_accuont(username, pwd)
    save_profile()
    



def check_info():
    try:
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
    except Exception as e:
        print('connecting error:', e)


def login(username, pwd):
    try:
        headers_login = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache'
        }
        cont_login = 'username={}&password={}&ac_id=1&action=login&type=1&n=100'
        req_body = cont_login.format(username, pwd)

        conn = http.client.HTTPConnection(target_ip, target_port)
        conn.request('POST', path_portal, req_body, headers_login)
        resp = conn.getresponse()
        response_text = str(resp.read(), 'utf-8')
        conn.close()
        return response_text
    except Exception as e:
        print('connecting error:', e)

def login_as(*num):
    if len(num) == 0:
        sel = profiles['accounts_sel']
    else:
        sel = num[0]

    if len(profiles['accounts']) > sel:
        username = profiles['accounts'][sel]['username']
        pwd = profiles['accounts'][sel]['pwd']
        return login(username, pwd)
    else:
        print('error in login_as(), num out of range')
        return 'Error: number out of range'

def logout(online_info):
    if 'username' in online_info:
        username = online_info['username']
        try:
            headers_logout = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache'
            }
            cont_logout = 'action=logout&ac_id=1&username={}&type=2'
            req_body = cont_logout.format(username)

            conn = http.client.HTTPConnection(target_ip, target_port)
            conn.request('POST', path_portal, req_body, headers_logout)
            resp = conn.getresponse()
            response_text = str(resp.read(), 'utf-8')
            conn.close()
            return response_text
        except Exception as e:
            print('connecting error:', e)
            return False
    else:
        return 'not online'

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

    for account in enumerate(profiles['accounts']):
        print('account {}: {}'.format(account[0], account[1]['username']))

    op = re.findall('\w+',
        input('input\naccount number to log in,\n"\
logout" to log out,\n\
"e" to exit program,\n\
"a" to append new account,\n\
others to check infomation:\n>>')
    )

    if len(op) == 0:
        continue

    
    if op[0] in ('e', 'q', 'exit', 'quit'):
        print('exit...')
        break

    elif op[0] in ('l', 'login', 'log in', 'log on') or re.match('\d+', op[0]):
        if online_info:
            print('you have already logged in')
        else:
            m = re.match('\d+', op[0])
            if m:
                sel = int(m.group(0))
            else:
                sel = profiles['accounts_sel']
            print('loging in as {}...'.format(profiles['accounts'][sel]['username']))
            response_text = login_as(sel)

            print(response_text)
            
            if response_text.startswith('login_ok'):
                print('succeeded logging in')
            else:
                m = re.search('\#((.*)\:(.*))', response_text)
                if m:
                    print('Error:', m.groups()[0])
                else:
                    print('Unknown error')

    elif op[0] in ('logout', 'log out'):
        if online_info:
            print('logging out...')

            response_text = logout(online_info)
            if response_text.startswith('logout_ok'):
                print('succeeded logging out')
            else:
                print('failing logging out,', response_text)
        else:
            print('not online')

    elif op[0] in ('a'):
        if len(op) < 3:
            account = require_account()
            add_accuont(account[0], account[1])
            save_profile()
        else:
            add_accuont(op[1], op[2])
            save_profile()
    else:
        pass
