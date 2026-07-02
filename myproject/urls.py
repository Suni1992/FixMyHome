from django.contrib import admin
from django.urls import path
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse

# व्यूज फ़ंक्शंस इम्पोर्ट करें
from leads.views import (
    lead_collection_view, 
    pincodes_view, 
    statistics_view, 
    about_view, 
    worker_card_view, 
    customer_card_view
)
from leads.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

def robots_txt_view(request):
    robots_content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Sitemap: https://fixmyhomes.in/sitemap.xml\n"
    )
    return HttpResponse(robots_content, content_type="text/plain")

urlpatterns = [
    # एडमिन रूट
    path('admin/', admin.site.urls),
    
    # मुख्य वेबसाइट रूट्स
    path('', lead_collection_view, name='lead_form'),
    path('pincodes/', pincodes_view, name='pincodes'),
    path('statistics/', statistics_view, name='statistics'),
    path('about/', about_view, name='about'),
    
    # 🎯 डायनेमिक डिजिटल कार्ड्स रूट्स (सुनील के नए कस्टमर और वर्कर आधारित कार्ड्स)
    path('card/worker/<int:lead_id>/', worker_card_view, name='worker_card'),
    path('card/customer/<int:lead_id>/', customer_card_view, name='customer_card'),
    
    # साइटमैप और रोबोट्स रूट्स
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt_view),
]