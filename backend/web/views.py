from core import models
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import logging
from django.db import IntegrityError
from . import filters

logger = logging.getLogger(__name__)

PAGE_SIZE = 10


@login_required
def customers(request):
    resp = None
    if request.method == 'POST':
        resp = action_pending(request)
        print(resp)
        return redirect('customers')
    qs = models.Customer.objects.all()
    f = filters.CustomerFilter(request.GET, queryset=qs)

    paginator = Paginator(f.qs, PAGE_SIZE)
    page = request.GET.get('page', 1)
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        customers = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        customers = paginator.page(page)
    ctx = {'page_obj': paginator.page(page), 'filter': f, 'customers': customers, }
    return render(request, 'web/customers.html', ctx)


@login_required
def payments(request):
    f = filters.PaymentFilter(request.POST, queryset=models.Payment.objects.all())
    return render(request, 'web/payments.html', {'payments': f})


@login_required
def file_entries(request):
    f = filters.FileEntryFilter(request.POST, queryset=models.FileEntry.objects.all())
    return render(request, 'web/file-entries.html', {'file_entries': f})


@login_required
def staff_users(request):
    return render(request, 'web/staff-users.html', {'users': User.objects.filter(is_staff=True)})


def action_pending(request):
    data = request.POST
    logger.debug("WhiteListApprovalView: %s", data)
    print(data)
    consumer = request.user.consumer

    try:
        if not consumer.user.is_staff:
            raise Exception('You must be Tigo staff to execute this API call')

        cust_id = data.get('id')
        cust = models.Customer.objects.get(id=cust_id)
        if not cust.request == 'Initiated':
            raise Exception('The customer is not in initiated state')
        if data.get('action') == 'Approved':
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
            logger.info(f'Successfully approved customer whitelist [{cust.command}] for customer: {cust_id}')
        elif data.get('action') == 'Rejected':  # Rejected
            if cust.command in ['DELETE', 'UPDATE']:
                new_status = 'Active'
            else:
                new_status = 'Removed'
                cust.owner_id = f'{cust.owner_id}_{cust.id}'
            cust.request = 'Rejected'
            cust.account_number_req = None
            cust.bank_id_req = None
            cust.status = new_status
            cust.save()
            logger.info(f'Successfully rejected customer whitelist [{cust.command}] for customer: {cust_id}')
        else:
            raise Exception('Invalid or no approval "action" provided')
    except Exception as ex:
        logger.error(ex)
        err_code = 906
        err_msg = f'Invalid request or missing details: {ex}'
        if 'unique constraint' in str(ex):
            err_code = 907
            err_msg = 'Duplicate entry detected, check your inputs and resubmit!'
        return {
            'result': err_code,
            'message': err_msg,
        }
    return {
        'result': 200,
        'message': f'Successfully executed the approval update'
    }
