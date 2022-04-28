from django.contrib import admin

from django.contrib.sitemaps.views import sitemap
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from shop_site import api, views
from shop_site.api import AdListFilter

from shop_site.views import AdsCreate
from sitemaps import AdSitemap

sitemaps = {
    'ads': AdSitemap
}



from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from shop_site.views import AdsList, AdsDetail, \
    SellerUpdateView, AdsCreate, AdsUpdateView



router = DefaultRouter()
router.register(r'ads', api.MyModelViewSet)
router.register(r'users', api.UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('seller/<int:pk>/', api.SellerUpdateViews.as_view()),
    path('accounts/', include('allauth.urls')),
    path('ads/add/', AdsCreate.as_view(), name='ads_create'),
    re_path('^adbasket/(?P<username>.+)/$', api.AdBasketList.as_view()),
    path('archive/', AdListFilter.as_view())
]

# urlpatterns = [
#     path('', include('shop_site.urls')),
#     path('accounts/', include('allauth.urls')),
#     # path(r'accounts/login/', include('django.contrib.auth.urls')),
#     path('admin/', admin.site.urls),
#     # path("ads/<int:pk>/", AdsDetail.as_view(), name='ads_detail'),
#     path('seller/<int:pk>/edit/', SellerUpdateView.as_view(), name='seller_data_edit'),
#     # path('ads/add/', AdsCreate.as_view(), name='ads_create'),
#     path('ads/<int:pk>/edit/', AdsUpdateView.as_view(), name='ads_data_edit'),
#     # path('', AdsList.as_view(), name='ad_list'),
#     path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
#          name='django.contrib.sitemaps.views.sitemap'),
#     re_path(r'^robots\.txt', include('robots.urls')),
#     path('', include('shop_site.urls')),
# ]

if settings.DEBUG:
    # import debug_toolbar

    urlpatterns = [
                      # path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
