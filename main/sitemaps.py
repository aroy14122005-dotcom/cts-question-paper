from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import SubjectPDF


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "search",
            "contact",
        ]

    def location(self, item):
        return reverse(item)


class SubjectPDFSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return SubjectPDF.objects.all().order_by("-uploaded_at")

    def lastmod(self, obj):
        return obj.uploaded_at

    def location(self, obj):
        return reverse(
            "paper_detail",
            kwargs={"slug": obj.slug}
        )