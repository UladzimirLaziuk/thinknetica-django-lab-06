from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import EmailMessage

from django.db.models.signals import post_save

from django.dispatch import receiver


def email_sends(**kwargs):
    from shop_site.models import Ad, Subscription
    sub_item = Subscription.objects.filter(title='new_ad')
    instance = kwargs['instance']
    from_email = 'admin@mysite'
    print(sub_item, instance)
    for item in set(sub_item):

        item_create = item.date_created
        to_email = item.user.email
        ad_list = Ad.objects.filter(data_create__gte=item_create).values_list('title', flat=True)
        if not to_email:
            continue
        subject = 'Новые объявления на сайте'
        html_content = '<p><i>Здравствуйте {}</i></p>'.format(item.user.username)
        html_content += 'Новое объявлеие на сайте: {}'.format(list(ad_list))
        html_content += '<p><i>Всего доброго.</i></p>'
        msg = EmailMessage(subject, html_content, from_email, [to_email])
        msg.content_subtype = "html"
        msg.send()


@receiver(post_save, sender='shop_site.Ad')
def email_shed(**kwargs):
    cron_sheduler = BackgroundScheduler()
    kwargs.update({'cron_sheduler': cron_sheduler})
    cron_sheduler.add_job(email_sends, 'cron', kwargs=kwargs, week='*', hour=19, minute=42)
    cron_sheduler.start()
