from core import sftp_connect as sftp
from config import config as cfg
from shutil import copyfile
import time
from core import secure_files as sf
import requests
import csv
from datetime import datetime


def generate_file(name):
    with open(f'{cfg.sftp_local_path()}/{name}', 'w') as f:
        csv_columns = ['CompanyID', 'Amount', 'ReferenceNumber']
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        i = 0
        ts = int(round(time.time() * 1000))
        for owner_id in [7, 8]:
            i += 1
            data = {
                'CompanyID': owner_id,
                'Amount': 1000,
                'ReferenceNumber': f'T{i}{ts}'
            }
            writer.writerow(data)


def run():
    t_stamp = int(round(time.time() * 1000))
    new_file = f'{t_stamp}_Payment.csv'
    generate_file(new_file)
    sftp.upload(new_file, cfg.sftp_tapsoa_path())
    sig = sf.sign(f'{cfg.sftp_local_path()}/{new_file}', '2020')
    print(sig)
    token = "HU3eV4AdXuzKqE2jNn7p5KGsybvVst"
    with open(f'{cfg.sftp_local_path()}/{new_file}') as csv_file:
        reader = csv.DictReader(csv_file)
        count = 0
        total = 0
        for row in reader:
            _, amount, _ = row['CompanyID'], row['Amount'], row['ReferenceNumber']
            count += 1
            total += float(amount)
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
        data = {
            "fileName": new_file,
            "timestamp": datetime.now().isoformat(timespec='minutes'),
            "fileReferenceId": f"TPS{t_stamp}",
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
