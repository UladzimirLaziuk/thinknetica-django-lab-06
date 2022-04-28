import json
import unittest

from django.contrib.auth.models import User

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.test import TestCase, modify_settings
from django.test import Client
from django.urls import reverse



from django.test import Client, TestCase

from django.test import RequestFactory, Client, TestCase


from django.urls import reverse

from shop_site.models import Ad, Tag


class TestAdsView(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self) -> None:
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

    def tearDown(self) -> None:
        self.client.logout()  # ??
        self.user.delete()

    def test_context(self):
        answer_login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(answer_login)
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
        self.assertIn('ad_list', response.context)
        self.assertTemplateUsed(response, 'main/ad_list.html')
        self.assertTrue(response.context_data['object_list'], Ad.objects.count)
        self.assertTrue(response.context_data['tag_list'], Tag.objects.count)

    def test_pagination(self):
        response = self.client.get('/')
        self.assertTrue('is_paginated' in response.context_data)
        self.assertTrue(response.context_data['is_paginated'], True)
        self.assertTrue(len(response.context_data['object_list']), 5)


#
class TestSellerUpdateView(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testpass'
        self.is_active = True
        email = 'jacob@mail.ru'
        self.user = User.objects.create_user(username=self.username, email=email)
        self.user.set_password(self.password)
        self.user.save()
        self.urls = reverse('seller_data_edit', kwargs={'pk': self.user.id})

    def tearDown(self) -> None:
        self.client.logout()
        self.user.delete()


    def test_call_view_deny_anonymous(self):
        response = self.client.get(self.urls, follow=True)
        self.assertRedirects(response, f'/accounts/login/?next=/seller/{self.user.id}/edit/')
        response = self.client.post(self.urls, follow=True)
        self.assertRedirects(response, f'/accounts/login/?next=/seller/{self.user.id}/edit/')

    def test_call_view_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("account_login"), follow=True)
        self.assertTemplateUsed(response, 'main/ad_list.html')

    def test_ajax_login_success(self):
        user = User.objects.create(username="john", is_active=True)
        user.set_password("doe")
        user.save()
        resp = self.client.post(
            reverse("account_login"),
            {"login": "john", "password": "doe"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode("utf8"))
        self.assertEqual(data["location"], "/")


class TestAdsUpdateView(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self) -> None:
        self.ad = Ad.objects.get(pk=1)

        self.client = Client()
        self.username = 'testuser'
        self.password = 'testpass'
        self.is_active = True
        self.email = 'jacob@mail.ru'
        self.user = User.objects.create_user(username=self.username, email=self.email)
        self.user.set_password(self.password)
        self.user.save()
        self.urls = reverse('ads_data_edit', kwargs={'pk': self.ad.id})

    def tearDown(self) -> None:
        self.client.logout()
        self.user.delete()

    def test_call_view_deny_anonymous(self):
        response = self.client.get(self.urls, follow=True)
        self.assertRedirects(response, '/accounts/login/')
        response = self.client.post(self.urls, follow=True)
        self.assertRedirects(response, '/accounts/login/')

    def test_call_view_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("account_login"), follow=True)
        self.assertTemplateUsed(response, 'main/ad_list.html')





class TestMidlewareDetect(unittest.TestCase):

    def test_http(self) -> None:
        c = Client(HTTP_USER_AGENT='mobile')
        response = c.get('')
        request_after_middleware = response.wsgi_request
        self.assertTrue(hasattr(request_after_middleware, 'is_mobile'))
        self.assertEqual(request_after_middleware.is_mobile, True)




if __name__ == '__name__':

    unittest.main()

