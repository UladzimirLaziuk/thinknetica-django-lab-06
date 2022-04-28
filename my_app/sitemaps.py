from django.contrib.sitemaps import Sitemap
from shop_site.models import Ad


class AdSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Ad.objects.filter(archive=False)

    def lastmod(self, obj):
        return obj.data_edit


