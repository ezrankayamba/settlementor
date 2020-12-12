from core import sftp_connect as sftp
from config import config as cfg
from shutil import copyfile
import time
from core import secure_files as sf
import requests
import csv


def run():
    file = 'test.csv'

    ts = int(round(time.time() * 1000))
    new_file = f'{ts}_{file}'
    copyfile(f'{cfg.sftp_local_path()}/{file}', f'{cfg.sftp_local_path()}/{new_file}')
    sftp.upload(new_file, cfg.sftp_tapsoa_path())
    # sftp.upload(cfg.sftp_tigo_path(), file)
    sig = sf.sign(f'{cfg.sftp_local_path()}/{new_file}', '2020')
    print(sig)
    token = "HU3eV4AdXuzKqE2jNn7p5KGsybvVst"
    with open(f'{cfg.sftp_local_path()}/{new_file}') as csv_file:
        reader = csv.DictReader(csv_file)
        count = 0
        total = 0
        for row in reader:
            company_id, amount, ref_number = row['CompanyID'], row['Amount'], row['ReferenceNumber']
            count += 1
            total += amount
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
        data = {
            "fileName": new_file,
            "timestamp": "2020-11-09 13:34:43",
            "fileReferenceId": f"TPS100001{ts}",
            "totalAmount": total,
            "countOfRecords": count,
            "fileSignature": sig
        }
        url = 'http://accessgwtest.tigo.co.tz:8080/LipiaMafuta2TigoFileShared'
        res = requests.post(url, json=data, headers=headers)
        if res.ok:
            print('Success: ', res.text)
        else:
            print('Fail', res.text)
