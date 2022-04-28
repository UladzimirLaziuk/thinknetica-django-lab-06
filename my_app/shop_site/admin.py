from django import forms
from django.contrib import admin
from shop_site.models import Seller, Category, SMSLog, Picture, Ad, Subscription

from django.contrib.flatpages.models import FlatPage
from ckeditor.widgets import CKEditorWidget

# Register your models here.

from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.admin import FlatpageForm


class NewFlatpageForm(FlatpageForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = FlatPage
        fields = '__all__'


class FlatPageAdminNew(FlatPageAdmin):
    form = NewFlatpageForm


class PersonAdmin(admin.ModelAdmin):
    list_display = ['user', 'qty_ad']


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('title',)
    exclude = 'ad',


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdminNew)
admin.site.register(Seller, PersonAdmin)
admin.site.register(Category)
admin.site.register(Picture)


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ("title", "data_create", "archive",)
    list_filter = ('tags', 'data_create')
    list_editable = ("archive",)
    actions = ['make_archival']

    def make_archival(self, request, queryset):
        queryset.update(archive=True)

    make_archival.short_description = "Send the selected ad to the archive"

admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(SMSLog)

