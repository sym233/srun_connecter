#python 3.5

import sys
import http.client
import json
import re

target_ip = '172.16.202.201'
target_port = 69

path_portal = '/cgi-bin/srun_portal'
path_info = '/cgi-bin/rad_user_info'

usr_name = ''
pwd = ''
# TODO: read username from file

if len(usr_name) == 0:
    usr_name = input('please input your username:\n')
if len(pwd) == 0:
    pwd = input('please input your password:\n')


def check_info():
    conn = http.client.HTTPConnection(target_ip, target_port)
    # connect
    conn.request('GET', path_info)
    resp = conn.getresponse()
    # response
    response_text = str(resp.read(), 'utf-8')
    conn.close()
    return response_text

def login(usr_name, pwd):
    headers_login = {'Content-Type': 'application/x-www-form-urlencoded',
'Cache-Control': 'no-cache'}
    cont_login = '''username={}&\
password={}&\
ac_id=1&\
action=login&\
type=1&\
n=100'''
    req_body = cont_login.format(usr_name, pwd)

    conn = http.client.HTTPConnection(target_ip, target_port)
    conn.request('POST', path_portal, req_body, headers_login)
    resp = conn.getresponse()
    response_text = str(resp.read(), 'utf-8')
    conn.close()
    return response_text

def logout(usr_name):
    headers_logout = {'Content-Type': 'application/x-www-form-urlencoded',
'Cache-Control': 'no-cache'}
    cont_logout = 'action=logout&ac_id=1&username={}&type=2'
    req_body = cont_logout.format(usr_name)

    conn = http.client.HTTPConnection(target_ip, target_port)
    conn.request('POST', path_portal, req_body, headers_logout)
    resp = conn.getresponse()
    response_text = str(resp.read(), 'utf-8')
    conn.close()
    return response_text


while True:
    op = input()

    response_text = check_info()
    print(response_text)
    
    is_online = (response_text != 'not_online')
    
    if op in ('e', 'q', 'exit', 'quit'):
        print('exit...')
        break

    elif op in ('login', 'log in', 'log on'):
        if is_online:
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
        if is_online:
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
    
