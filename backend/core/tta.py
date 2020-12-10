import xml.etree.ElementTree as ET
import requests
import re
import xmltodict as xml
from config import config as cfg


pattern = re.compile(r'\s+')


def pay_settlement(ref_number,   bank_account,  amount, bank_id='CRDB',  terminal_type='API'):
    username, password, brand_id = cfg.consumer_data()
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
            trans_id = res['param11']
            return (0, trans_id)
        else:
            print('Failed: ', result, ':', message)
            return (result, None)
    else:
        print('Failed: ', res.status_code)
    return (-1, None)


def check_balance(terminal_type='API'):
    username, password, brand_id = cfg.consumer_data()
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
    try:
        res = requests.post(cfg.bal_url(), req_xml, headers=headers)
        if res.ok:
            res_xml = res.text
            res = xml.parse(res_xml)['TCSReply']
            result = int(res['Result'])
            message = res['Message']
            if result == 0:
                balance = res['param1']
                return (0, balance)
            else:
                print('Failed: ', result, ':', message)

        else:
            print('Failed: ', res.status_code)
        return (-1, 'Fail')
    except Exception as ex:
        return (-2, ex)
