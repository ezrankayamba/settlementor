import xml.etree.ElementTree as ET
import requests
import re
import xmltodict as xml
pattern = re.compile(r'\s+')

TELEPIN_URL = 'http://10.99.1.161:6060/TELEPIN'


def pay_settlement(username, password,  bank_account,  amount, bank_id='CRDB', brand_id='1071', terminal_type='WEB'):
    req_xml = f'''
        <TCSRequest>
            <UserName>{username}</UserName>
            <Password>{password}</Password>
            <TERMINALTYPE>{terminal_type}</TERMINALTYPE>
            <Function name="TOPUP">
                <param1>{bank_id}</param1>
                <param2>{amount}</param2>
                <param5>{brand_id}</param5>
                <param11>{bank_account}</param11>
            </Function>
        </TCSRequest>
    '''
    print(req_xml)
    headers = {
        'Content-Type': 'text/xml'
    }
    res = requests.post(TELEPIN_URL, req_xml, headers=headers)
    if res.ok:
        res_xml = res.text
        print(res_xml)
        res = xml.parse(res_xml)['TCSReply']
        print(res)
        result = int(res['Result'])
        message = res['Message']
        if result == 0:
            print('Success: ', '0:', message)
        else:
            print('Failed: ', result, ':', message)

    else:
        print('Failed: ', res.status_code)


def check_balance(username, password, terminal_type='WEB'):
    req_xml = f'''
        <TCSRequest>
            <UserName>{username}</UserName>
            <Password>{password}</Password>
            <TERMINALTYPE>{terminal_type}</TERMINALTYPE>
            <Function name="BALANCEMWALLET"></Function>
        </TCSRequest>
    '''
    print(req_xml)
    headers = {
        'Content-Type': 'text/xml'
    }
    res = requests.post(TELEPIN_URL, req_xml, headers=headers)
    if res.ok:
        res_xml = res.text
        print(res_xml)
        res = xml.parse(res_xml)['TCSReply']
        print(res)
        result = int(res['Result'])
        message = res['Message']
        balance = res['param1']
        if result == 0:
            print('Success: ', '0:', message)
            print('Balance: ', balance)
        else:
            print('Failed: ', result, ':', message)

    else:
        print('Failed: ', res.status_code)
