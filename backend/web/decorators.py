from datetime import timedelta
from django.shortcuts import render, redirect


def otp_required(view_func):
    def wrap(request, *args, **kwargs):
        print(request, args, kwargs)
        if request.session.get('otp-verified', False):
            return view_func(request, *args, **kwargs)
        return redirect('verify-otp')
    wrap.__doc__ = view_func.__doc__
    wrap.__name__ = view_func.__name__
    return wrap
