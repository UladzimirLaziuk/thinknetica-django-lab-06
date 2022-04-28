from __future__ import absolute_import, unicode_literals

import logging
import os
import smtplib

from django.core.mail import EmailMessage

from celery.utils.log import get_task_logger

from my_app.celery import app

logger = get_task_logger(__name__)

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


@app.task(bind=True, default_retry_delay=5 * 60)
def send_email_task(self, *args, **kwargs):
    logger.info("in task")
    from shop_site.models import Ad, Subscription
    sub_item = Subscription.objects.filter(title='new_ad')
    from_email = 'admin@mysite'
    for item in set(sub_item):
        item_create = item.date_created
        to_email = item.user.email
        ad_list = Ad.objects.filter(data_create__gte=item_create)\
            .values_list('title', flat=True)
        if not to_email:
            logger.info("%s no email address" % item.user)
            continue
        logger.info("%s email send" % item.user)
        subject = 'Новые объявления на сайте'
        html_content = '<p><i>Здравствуйте {}</i></p>'.format(item.user.username)
        html_content += 'Новое объявлеие на сайте: {}'.format(list(ad_list))
        html_content += '<p><i>Всего доброго.</i></p>'
        msg = EmailMessage(subject, html_content, from_email, [to_email])
        msg.content_subtype = "html"
        try:
            msg.send(fail_silently=False)
        except smtplib.SMTPException as ex:
            logger.error("%s error" % ex)
            self.retry(exc=ex, countdown=20)



@app.task(bind=True, default_retry_delay=5 * 60)
def send_sms_task(self, to_phone, code, sms_log_obj_id, *args, **kwargs):
    logger.info("in task")
    from twilio.rest import Client
    from shop_site.models import SMSLog
    account_sid = os.getenv('account_sid')
    auth_token = os.getenv('auth_token')
    messaging_service_sid = os.getenv('messaging_service_sid')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        messaging_service_sid=messaging_service_sid,
        body=code,
        to=to_phone
    )
    logger.info("Send sms %s" % to_phone)
    logger.info("Send sms %s" % message.status)


    sms_obj = SMSLog.objects.get(pk=sms_log_obj_id)
    sms_obj.response = message.status
    sms_obj.save()


