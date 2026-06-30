from django.contrib import admin
from django.urls import path
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView  # 🤖 robots.txt को डायरेक्ट लोड करने के लिए

# आपके leads ऐप के सभी व्यूज
from leads.views import lead_collection_view, pincodes_view, statistics_view, about_view

## हमने जो leads/sitemaps.py बनाया था, उसमें से StaticViewSitemap को इम्पोर्ट कर रहे हैं
from leads.sitemaps import StaticViewSitemap

# गूगल क्रॉलर को बताने के लिए साइटमैप की डिक्शनरी तैयार करना
sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    # 1. डैंगो का मुख्य एडमिन पैनल
    path('admin/', admin.site.urls),
    
    # 2. आपके leads ऐप की सभी मुख्य यूआरएल सेटिंग्स
    path('', lead_collection_view, name='lead_form'),
    path('pincodes/', pincodes_view, name='pincodes'),  # यह URL पिनकोड्स पेज के लिए है
    path('statistics/', statistics_view, name='statistics'),  # यह URL स्टेटिस्टिक्स पेज के लिए है
    path('about/', about_view, name='about'),  # यह URL एबाउट पेज के लिए है
    
    # 3. 🎯 गूगल सर्च क्रॉलर के लिए साइटमैप यूआरएल (sitemap.xml)
    # जब गूगल आपकी साइट पर आकर 'fixmyhomes.in/sitemap.xml' ढूंढेगा, तो डैंगो उसे यह साइटमैप दिखाएगा
    path(
        'sitemap.xml', 
        sitemap, 
        {'sitemaps': sitemaps}, 
        name='django.contrib.sitemaps.views.sitemap'
    ),
    
    # 4. 🤖 गूगल बॉट्स के निर्देशों के लिए robots.txt पाथ
    path(
        'robots.txt', 
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain")
    ),
]