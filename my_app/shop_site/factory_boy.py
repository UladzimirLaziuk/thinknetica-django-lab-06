from shop_site import models
from django.db.models.signals import post_save
import factory
from faker import Faker

faker = Faker()


class UserSeqFactory(factory.Factory):
    class Meta:
        model = models.User

    username = factory.Sequence(lambda n: 'FactoryBoyz' + 'z' * n)
    phone = factory.Sequence(lambda n: '123-555-%04d' % n)


class MyBaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.BaseModel
        abstract = True

    title = faker.text()


class CategoryFactory(MyBaseFactory):
    class Meta:
        model = models.Category


@factory.django.mute_signals(post_save)
class SellerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Seller
        django_get_or_create = ('user',)

    user = factory.SubFactory('shop_site.factory_boy.UserFactory')
    phone = factory.Sequence(lambda n: '123-555-%04d' % n)


@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: "user_%d" % n)

#
# class TagFactory(MyBaseFactory):
#     class Meta:
#         model = models.Tag


class AdFactory(MyBaseFactory):
    class Meta:
        model = models.Ad

    category = factory.SubFactory('shop_site.factory_boy.CategoryFactory')
    price = faker.pyint(10, 100)

    seller = factory.SubFactory('shop_site.factory_boy.SellerFactory')
    tags = []



    # @factory.post_generation
    # def tags(self, create, extracted, **kwargs):
    #     if not create:
    #         return
    #     if extracted:
    #         for tag in extracted:
    #             self.tags.add(tag)


