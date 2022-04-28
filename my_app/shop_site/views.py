import itertools
import logging


import random
import functools


from django.contrib.postgres.search import SearchVector


from django.core.cache.backends.base import DEFAULT_TIMEOUT


from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import MiddlewareNotUsed




from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser, User

from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.exceptions import MiddlewareNotUsed
from django.contrib.auth.models import AnonymousUser
# from django.core.exceptions import MiddlewareNotUsed

from django.shortcuts import render, get_object_or_404, redirect
from constance import config
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
# from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from my_app import settings
from shop_site.forms import SellerForm, UserForm, ImageFormSet, VerifyForm
from shop_site.models import Ad, Seller, SMSLog

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required



# Create your views here.
from shop_site.tasks import send_sms_task
from django.core.cache import cache

my_logger = logging.getLogger(__name__)
my_logger.setLevel(logging.DEBUG)


def index(request):
    turn_on_block = config.MAINTENANCE_MODE
    str_reverse = config.REVERSE_STRING
    user_name = request.user.username
    return render(request, 'main/index.html', context={'turn_on_block': turn_on_block, 'user_name': user_name,
                                                       'str_reverse': str_reverse})


class MiddlewareProb(MiddlewareMixin):
    template_reverse = ''

    def __init__(self, *args):
        super().__init__(*args)
        raise MiddlewareNotUsed()

    def process_request(self, request):
        if isinstance(request.user, AnonymousUser):
            return render(request, self.template_reverse or 'main/index.html', {})



# @method_decorator(permission_required('shop_site.view_ad', login_url='/accounts/login/'), name='dispatch')



# @method_decorator(permission_required('shop_site.view_ad', login_url='/accounts/login/'), name='dispatch')


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


# @method_decorator(cache_page(CACHE_TTL), name='dispatch')
class AdsList(ListView):
    model = Ad
    template_name = 'main/ad_list.html'
    paginate_by = 5
    ordering = ['data_create']

    # login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        query_tags_filter = Ad.objects.values_list('tags', flat=True)
        kwargs.update({'tag_list': itertools.chain(*query_tags_filter)})
        context = super().get_context_data(**kwargs)
        context['str_reverse'] = config.REVERSE_STRING
        context['turn_on_block'] = config.MAINTENANCE_MODE
        return context

    def get_queryset(self):
        tags_name = self.request.GET.get('tags_name')
        if tags_name:
            # self.queryset = self.model.objects.filter(tags__contains=[tags_name])
            self.queryset = self.model.objects.annotate(search=SearchVector('tags'),).filter(search=[tags_name])
        return super().get_queryset()


def for_cache_decorator(method):
    @functools.wraps(method)
    def wrapper(self, **kwargs):
        obj_context = kwargs.get('object')
        obj_context.price = getattr(obj_context, 'price') * random.randint(8, 12) / 10
        kwargs['object'] = obj_context
        object_cache = cache.get('object')
        if object_cache is None:
            cache.set('object', obj_context, timeout=60)
        return method(self, **kwargs)

    return wrapper


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AdsDetail(DetailView):
    model = Ad
    template_name = 'main/detail_ads.html'

    @for_cache_decorator
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(kwargs)
        return context



@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class SellerUpdateView(UpdateView):
    model = Seller
    template_name = 'seller_update.html'
    success_url = "ad_list"
    form_class = UserForm
    formset_class = SellerForm

    def get_context_data(self, *args, **kwargs):
        obj_for_update = self.get_object()
        kwargs.update({'form': UserForm(instance=obj_for_update.user)})
        kwargs.update({'form_set': SellerForm(instance=obj_for_update)})
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        question_formset = get_object_or_404(self.formset_class.Meta.model, user_id=self.kwargs['pk'])
        form_set = self.formset_class(request.POST, instance=question_formset)

        question_form = get_object_or_404(self.form_class.Meta.model, id=request.user.id)
        form = self.form_class(request.POST, instance=question_form)
        forms_code = VerifyForm()
        if form.is_valid() and form_set.is_valid():
            my_logger.debug('Valid - %s' % request.POST.get('phone'))

            if request.POST.get('phone'):
                sms_log_obj, creates = SMSLog.objects.get_or_create(seller=self.object)
                forms_code.is_valid()
                if request.POST.get('code') and request.POST.get('code').isdigit():

                    code = request.POST.get('code')
                    if sms_log_obj.code == int(code):
                        sms_log_obj.confirmed = True
                        sms_log_obj.save()

                if not sms_log_obj.confirmed:
                    to_phone = request.POST.get('phone')
                    sms_task_delay(to_phone, sms_log_obj.code, sms_log_obj.id)

                    return self.return_response_form(form_set, forms_code)
        return redirect(reverse("ad_list"))

    def return_response_form(self, form_set, forms_code, **kwargs):
        context = super().get_context_data(**{'form_set': form_set,
                                              'forms_code': forms_code}, **kwargs)
        return super().render_to_response(context)

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def form_invalid(self, form, form_set, **kwargs):
        context = super().get_context_data(form=form,
                                           form_set=form_set, **kwargs)
        return self.render_to_response(context)


def sms_task_delay(to_phone, code, sms_log_obj_id):
    my_logger.debug('%s to phone, code-%s' % (to_phone, code))
    answer_message = send_sms_task.delay(to_phone, str(code), sms_log_obj_id)
    return answer_message


class AdsCreate(CreateView):
    model = Ad
    fields = '__all__'
    template_name = 'ads_create.html'
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        return redirect('/accounts/login/')


class AdsUpdateView(UpdateView):
    model = Ad
    fields = 'title', 'price',
    template_name = 'ad_update.html'
    success_url = "ad_list"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        return redirect('/accounts/login/')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = ImageFormSet(self.request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  formset=formset))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formset = ImageFormSet()
        context['formset'] = formset
        return context

    def form_valid(self, form, formset):
        obj_query = self.set_objects_queryset()
        obj_query.update(**form.cleaned_data)
        formsets = formset.save(commit=False)
        for frs in formsets:
            frs.ad_link = obj_query.get()
            frs.save()
        return redirect(reverse("ad_list"))

    def set_objects_queryset(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        obj = self.model.objects.filter(pk=pk)
        return obj
