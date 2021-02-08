from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.response import Response
from core import models, tta
import logging
from django.db import IntegrityError

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
                params['request'] = 'Initiated'
                models.Customer.objects.create(**params)
            elif command == 'UPDATE':
                cust = models.Customer.objects.filter(owner_id=owner_id, consumer=consumer, status='Active').first()
                if cust:
                    cust.account_number_req = data['bankAccountNumber']
                    cust.bank_id_req = data['bankId']
                    cust.command = command
                    cust.request = 'Initiated'
                    cust.save()
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
            params = {
                'file_name_in': f_name,
                'timestamp': data['timestamp'],
                'file_reference_id': f_ref_id,
                'total_amount': data['totalAmount'],
                'count_of_records': data['countOfRecords'],
                'consumer': consumer,
                'signature': data['fileSignature'],
            }
            models.FileEntry.objects.create(**params)
        except Exception as ex:
            logger.error(ex)
            err_code = 906
            err_msg = f'Invalid request or missing details: {ex}'
            if 'unique constraint' in str(ex):
                err_code = 907
                err_msg = 'Duplicate entry detected, check your inputs and resubmit!'
            return Response({
                'result': err_code,
                'message': err_msg,
            })

        return Response({
            'result': 200,
            'message': f'Successfully executed the payment file notification',
            'fileReferenceId': f_ref_id
        })


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
            return Response({
                'result': err_code,
                'message': err_msg,
            })

        return Response({
            'result': 200,
            'message': f'Successfully executed the approval update'
        })
