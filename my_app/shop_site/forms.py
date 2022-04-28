from django.contrib.auth.models import User
from django.forms import ModelForm
from shop_site.models import Seller, Ad, Picture
from django.forms import inlineformset_factory
from allauth.account.forms import LoginForm
from allauth.account.forms import SignupForm
from django import forms
import phonenumbers


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'email'


class SellerForm(ModelForm):
    class Meta:
        model = Seller
        fields = 'itn', 'phone'

    def clean_phone(self):
        data = self.cleaned_data['phone']
        if data and not phonenumbers.is_valid_number(data):
            msg = "Данный phone не соответствует требованиям!"
            self.add_error('phone', msg)
        return data


ImageFormSet = inlineformset_factory(Ad, Picture,
                                     fields=('title', 'img_ads',), extra=1)


class MyCustomLoginForm(LoginForm):

    def login(self, *args, **kwargs):
        # Add your own processing here.
        # You must return the original result.
        return super(MyCustomLoginForm, self).login(*args, **kwargs)


class MyCustomSignupForm(SignupForm):

    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(MyCustomSignupForm, self).save(request)
        # Add your own processing here.
        # You must return the original result.
        return user


class VerifyForm(forms.Form):
    code = forms.IntegerField(label='Please Enter code here from sms', widget=forms.TextInput())
