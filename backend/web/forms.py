from django import forms


class OTPForm(forms.Form):
    otp = forms.CharField(label='Enter OTP', max_length=20, required=False)
