from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.response import Response
from core import models, tta
import logging
from django.db import IntegrityError
from core import tta
from core import sftp_connect as sftp
from config import config as cfg
from core import secure_files as sf
from core import secure_store as ss
import csv

logger = logging.getLogger(__name__)


class WhitelistView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    required_scopes = []

    def post(self, request, format=None):
        data = request.data
        logger.debug("WhitelistView: %s", data)
        owner_id = data['companyID']
        consumer = request.user.consumer
        command = data['command']

        params = {
            'owner_id': data['companyID'],
            'owner_name': data['companyName'],
            'bank_id': data['bankId'],
            'account_number': data['bankAccountNumber'],
            'consumer': consumer,
            'command': command
        }

        try:
            if command == 'ADD':
                for key in params:
                    if not params[key]:
                        raise Exception('Invalid or empty data')
                params['request'] = 'Initiated'
                models.Customer.objects.create(**params)
            elif command == 'UPDATE':
                cust = models.Customer.objects.filter(owner_id=owner_id, consumer=consumer, status='Active').first()
                if cust:
                    acc_num = data['bankAccountNumber']
                    bank_id = data['bankId']
                    if acc_num and bank_id:
                        cust.account_number_req = acc_num
                        cust.bank_id_req = bank_id
                        cust.command = command
                        cust.request = 'Initiated'
                        cust.save()
                    else:
                        raise Exception('Invalid or empty data')
                else:
                    raise Exception('Customer not found')
            elif command == 'REMOVE':
                cust = models.Customer.objects.filter(owner_id=owner_id, consumer=consumer, status='Active').first()
                if cust:
                    cust.command = command
                    cust.request = 'Initiated'
                    cust.account_number_req = None
                    cust.bank_id_req = None
                    cust.save()
                else:
                    raise Exception('Customer not found')
            else:
                return Response({
                    'result': 905,
                    'message': f'Unknown command {command}'
                })
        except Exception as ex:
            logger.error(ex)
            err_code = 906
            err_msg = f'Invalid request or missing details: {ex}'
            if 'unique constraint' in str(ex):
                err_code = 907
                err_msg = 'Duplicate entry detected, check your inputs and resubmit!'
            logger.error(f'{err_code}: {err_msg}')
            return Response({
                'result': err_code,
                'message': err_msg,
            })

        return Response({
            'result': 200,
            'message': f'Successfully executed {command} on the whitelist'
        })


class PaymentFileSharedView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    required_scopes = []

    def post(self, request, format=None):
        data = request.data
        logger.debug("PaymentFileSharedView: %s", data)
        consumer = request.user.consumer
        f_ref_id = None
        try:
            f_ref_id = data['fileReferenceId']
            f_name = data['fileName']
            total_amount = data['totalAmount']
            status, bal_or_msg = tta.check_balance()
            logger.debug(f'{status} - {bal_or_msg}')
            if status != 0:
                raise Exception(f"Not able to fetch balance of the collection account: {status}")
            if total_amount > float(bal_or_msg):
                raise Exception(f'Balance not enough: {bal_or_msg}/{total_amount}')
            if not sftp.download(cfg.sftp_tapsoa_path(), f_name):
                raise Exception('File does not exist')
            path = f'files/{f_name}'
            sig = data['fileSignature']
            with open(path) as csv_file:
                verified = sf.verify(path, sig)
                logger.debug(f'Verified:  {verified}')
                if not verified:
                    raise Exception('Signature not valid!')
                logger.debug('Successfully verified the signature. Continue with payment')
                reader = csv.DictReader(csv_file)
                headers = reader.fieldnames
                logger.debug(headers)
                required_cols = ['CompanyID', 'Amount', 'ReferenceNumber']
                logger.debug(required_cols)
                if not set(required_cols).issubset(set(headers)):
                    raise Exception('Invalid file format')

            params = {
                'file_name_in': f_name,
                'timestamp': data['timestamp'],
                'file_reference_id': f_ref_id,
                'total_amount': data['totalAmount'],
                'count_of_records': data['countOfRecords'],
                'consumer': consumer,
                'signature': sig,
            }
            logger.debug(params)
            models.FileEntry.objects.create(**params)
        except Exception as ex:
            logger.error(ex)
            err_code = 906
            err_msg = f'Invalid request or missing details: {ex}'
            if 'unique constraint' in str(ex):
                err_code = 907
                err_msg = 'Duplicate entry detected, check your inputs and resubmit!'
            res = {
                'result': err_code,
                'message': err_msg,
            }
            logger.debug(res)
            return Response(res)
        {
            'result': 200,
            'message': f'Successfully executed the payment file notification',
            'fileReferenceId': f_ref_id
        }
        logger.debug(res)
        return Response(res)


class WhiteListApprovalView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    required_scopes = []

    def post(self, request, format=None):
        data = request.data
        logger.debug("WhiteListApprovalView: %s", data)
        consumer = request.user.consumer

        try:
            if not consumer.user.is_staff:
                raise Exception('You must be Tigo staff to execute this API call')

            owner_id = data['companyID']
            cust = models.Customer.objects.get(owner_id=owner_id)
            if not cust.request == 'Initiated':
                raise Exception('The customer is not in initiated state')
            if data['status'] == 'Approved':
                cust.request = 'Approved'
                if cust.command in ['ADD', 'UPDATE']:
                    new_status = 'Active'
                    if cust.command == 'UPDATE':
                        cust.account_number = cust.account_number_req
                        cust.bank_id = cust.bank_id_req
                        cust.account_number_req = None
                        cust.bank_id_req = None
                else:  # Remove
                    new_status = 'Removed'
                cust.status = new_status
                cust.save()
                logger.info(f'Successfully approved customer whitelist [{cust.command}] for customer: {owner_id}')
            elif data['status'] == 'Rejected':  # Rejected
                cust.request = 'Rejected'
                cust.account_number_req = None
                cust.bank_id_req = None
                cust.save()
                logger.info(f'Successfully rejected customer whitelist [{cust.command}] for customer: {owner_id}')
            else:
                raise Exception('Invalid or no approval "status" provided')
        except Exception as ex:
            logger.error(ex)
            err_code = 906
            err_msg = f'Invalid request or missing details: {ex}'
            if 'unique constraint' in str(ex):
                err_code = 907
                err_msg = 'Duplicate entry detected, check your inputs and resubmit!'
            res = {
                'result': err_code,
                'message': err_msg,
            }
            logger.debug(res)
            return Response(res)
        res = {
            'result': 200,
            'message': f'Successfully executed the approval update'
        }
        logger.debug(res)
        return Response(res)
