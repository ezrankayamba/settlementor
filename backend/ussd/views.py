from django.shortcuts import render
from ussd import models
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt


def menu_navigate(request):
    print(request.POST, request.GET)
    return 'Hello'


def ussd_home(request):
    ctx = {}
    return render(request, 'ussd/ussd.html', ctx)


@csrf_exempt
def menus(request):
    if request.method == 'POST':
        print(request.POST)
    menus = models.Menu.objects.all()
    print('Menus', menus)
    return JsonResponse({
        'result': 0,
        'message': 'Success',
        'data': serializers.serialize('json', menus)
    })
