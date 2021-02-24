import pandas as pd
from datetime import datetime


def convert(file, num):
    df = pd.read_excel(file)
    mapping = {
        'SO#': 'Transfer_ID',
        'Destination MSISDN': 'Refer_Number',
        'TRX Time': 'Trans_Date',
        'Type': 'Prev Balance',
        'Source Amount': 'Post Bal',
        'D.Amount': 'Amount',
        'Suffix': 'Transfer_Status',
        'Terminal': 'MoneyPayer/Receiver',
        'Brand': 'Account',
        'Ref': 'Original_Txn_ID',
        'Status': 'Status_Change_date'
    }
    df = df.rename(columns=mapping)
    columns = list(map(lambda x: x, mapping.values()))
    df = df[columns]
    df['Prev Balance'] = 0
    df['Post Bal'] = 0
    df['Status_Change_date'] = None
    df['Original_Txn_ID'] = None
    print(columns)

    print(df.head())
    today = datetime.today().strftime('%Y%m%d')
    fname = f'out/LipiaMafuta_{today}_{num:02}.csv'
    df.to_csv(fname, index=False)


if __name__ == '__main__':
    file = r'files/Lipia_mafuta24.xls'
    num = 2
    convert(file, num)
