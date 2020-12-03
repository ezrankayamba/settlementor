from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.response import Response
from core import models
import logging

logger = logging.getLogger(__name__)


class WhitelistView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    required_scopes = []

    def post(self, request, format=None):
        data = request.data
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
                cust.account_number_req = data['bankAccountNumber']
                cust.bank_id_req = data['bankId']
                cust.command = command
                cust.request = 'Initiated'
                cust.save()
            elif command == 'REMOVE':
                cust = models.Customer.objects.filter(owner_id=owner_id, consumer=consumer, status='Active').first()
                # cust.delete()
                cust.command = command
                cust.request = 'Initiated'
                cust.account_number_req = None
                cust.bank_id_req = None
                cust.save()
            else:
                return Response({
                    'result': 905,
                    'message': f'Unknown command {command}'
                })
        except Exception as ex:
            logger.error(ex)
            return Response({
                'result': 906,
                'message': f'Invalid request details or customer is not active'
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
        consumer = request.user.consumer
        f_ref_id = data['fileReferenceId']
        f_name = data['fileName']
        params = {
            'file_name': f_name,
            'timestamp': data['timestamp'],
            'file_reference_id': f_ref_id,
            'total_amount': data['totalAmount'],
            'count_of_records': data['countOfRecords'],
            'consumer': consumer,
        }
        try:
            models.FileEntry.objects.create(**params)
        except Exception as ex:
            logger.error(ex)
            return Response({
                'result': 906,
                'message': f'Invalid request details: {ex}',
                'fileReferenceId': f_ref_id
            })

        return Response({
            'result': 200,
            'message': f'Successfully executed the payment file notification',
            'fileReferenceId': f_ref_id
        })
