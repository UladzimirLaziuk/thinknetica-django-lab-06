
from django.contrib.postgres.fields import ArrayField
from django.core.mail import EmailMessage

import os



from django.core.mail import EmailMessage, EmailMultiAlternatives

from django.db import models
from autoslug import AutoSlugField

from shop_site.signals import new_signal

# Create your models here.

from django.db.models.signals import post_save
from django.dispatch import receiver


from django.dispatch import receiver
from django.template.loader import render_to_string




import random

from random import random

from django.core.mail import EmailMessage, EmailMultiAlternatives

from django.db import models
from autoslug import AutoSlugField


from phonenumber_field.modelfields import PhoneNumberField


from shop_site.signals import new_signal

from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.


from django.db.models.signals import post_save
from django.dispatch import receiver

from django.dispatch import receiver
from django.template.loader import render_to_string


from django.urls import reverse
from sorl.thumbnail import ImageField
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from shop_site.signals import new_signal





from shop_site.signals import new_signal




class BaseModel(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.title}'


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    itn = models.CharField(max_length=255, blank=True)
    logo = ImageField(upload_to='image/', default="image/pingvin_Shkiper.jpg")
    phone = PhoneNumberField(blank=True)

    @property
    def seller_id(self):
        return self.user.id

    @property
    def seller_name(self):
        return self.user.username

    @property
    def qty_ad(self):
        return self.seller_ad.count()

    def __str__(self):
        return f'{self.user.username}'


class Category(BaseModel):
    # title = models.CharField(max_length=255, verbose_name='Название категории')
    slug = AutoSlugField(populate_from='title', unique=True)


class Ad(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='seller_ad')
    data_create = models.DateTimeField(auto_now_add=True)
    data_edit = models.DateTimeField(auto_now=True)
    tags = ArrayField(models.CharField(max_length=200, blank=True), blank=True)
    price = models.PositiveIntegerField(default=0, verbose_name='Цена')
    archive = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("ads_detail", kwargs={"pk": self.id})



    def save(self, *args, **kwargs):
        super().save()
        result_msg = new_signal.send(sender=self.__class__, instance=self)



class ArchiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archive=True)


class ArchiveAds(Ad):
    objects = ArchiveManager()

    class Meta:
        proxy = True


class Picture(BaseModel):
    ad_link = models.ForeignKey(Ad, on_delete=models.CASCADE, default=1)
    img_ads = ImageField(upload_to='image/', default="image/pingvin_Shkiper.jpg")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name='common users')
        instance.groups.add(group)


class Subscription(models.Model):
    SUBSCRIPTION_CHOICES = (
        ('new_ad', 'new_ad'),
    )
    title = models.CharField(max_length=9,
                             choices=SUBSCRIPTION_CHOICES)
    user = models.ForeignKey(User, related_name="subscriptions", on_delete=models.CASCADE)
    ad = models.ManyToManyField(Ad, related_name="ad_sub", blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.title)


@receiver(new_signal, sender=Ad)
def subscribe_message(sender, instance, **kwargs):
    from_email = 'admin@mysite'
    sub_item = Subscription.objects.filter(title__search='new_ad')
    if not sub_item:
        return 'Not Subscriptions'
    for item in sub_item:
        to_email = item.user.email
        if not to_email:
            continue
        subject = 'Новое объявлеие на сайте'
        html_content = '<p><i>Здравствуйте {}</i></p>'.format(item.user.username)
        html_content += 'Новое объявлеие на сайте: {}'.format(instance.title)
        html_content += '<p><i>Всего доброго.</i></p>'
        msg = EmailMessage(subject, html_content, from_email, [to_email])
        msg.content_subtype = "html"
        return msg.send()



def code_generator():
    return ''.join([str(random.randint(0, 9)) for _ in range(4)])


class SMSLog(models.Model):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    code = models.IntegerField(default=code_generator)


    response = models.CharField(max_length=255, default='No')



