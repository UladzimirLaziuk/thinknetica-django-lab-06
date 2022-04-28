from rest_framework import serializers
from django.contrib.auth.models import User
from shop_site.models import Ad, Category, Seller


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']


class AdSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="title", queryset=Category.objects.all())
    seller = serializers.SlugRelatedField(read_only=True, slug_field="seller_name")
    ad_detail = serializers.HyperlinkedIdentityField(view_name='ad-detail')
    tags = serializers.ListField(child=serializers.CharField(required=False))  # TODO

    class Meta:
        model = Ad
        fields = ("title", "seller", "category", "ad_detail", 'tags')



class SellerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Seller
        fields = "__all__"

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user
        user.username = user_data.get('username', instance.user.username)
        user.save()
        instance.phone = validated_data.get('phone', instance.phone)
        instance.itn = validated_data.get('itn', instance.itn)
        instance.save()
        return instance



