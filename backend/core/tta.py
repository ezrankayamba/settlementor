import xml.etree.ElementTree as ET
import requests
import re
import xmltodict as xml
from config import config as cfg


pattern = re.compile(r'\s+')


def pay_settlement(ref_number, username, password,  bank_account,  amount, bank_id='CRDB', brand_id='1071', terminal_type='WEB'):
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
                <param12>{ref_number}</param12>
            </Function>
        </TCSRequest>
    '''
    print(req_xml)
    headers = {
        'Content-Type': 'text/xml'
    }

    res = requests.post(cfg.tta_url(), req_xml, headers=headers)
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
            <Function name="BALANCEMWALLET">
                <param1>Not applicable</param1>
            </Function>
        </TCSRequest>
    '''
    print(req_xml)
    headers = {
        'Content-Type': 'text/xml'
    }
    res = requests.post(cfg.bal_url(), req_xml, headers=headers)
    if res.ok:
        res_xml = res.text
        print(res_xml)
        res = xml.parse(res_xml)['TCSReply']
        print(res)
        result = int(res['Result'])
        message = res['Message']

        if result == 0:
            balance = res['param1']
            print('Success: ', '0:', message)
            print('Balance: ', balance)
        else:
            print('Failed: ', result, ':', message)

    else:
        print('Failed: ', res.status_code)
