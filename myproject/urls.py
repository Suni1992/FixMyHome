from django.contrib import admin
from django.urls import path
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse  # 🚀 robots.txt को डायरेक्ट टेक्स्ट रिस्पॉन्स भेजने के लिए

# आपके leads ऐप के सभी व्यूज (business_card_view यहाँ जोड़ा गया है)
from leads.views import lead_collection_view, pincodes_view, statistics_view, about_view, business_card_view

# हमने जो leads/sitemaps.py बनाया था, उसमें से StaticViewSitemap को इम्पोर्ट कर रहे हैं
from leads.sitemaps import StaticViewSitemap

# गूगल क्रॉलर को बताने के लिए साइटमैप की डिक्शनरी तैयार करना
sitemaps = {
    'static': StaticViewSitemap,
}

# 🤖 बिना किसी टेम्पलेट फ़ाइल के robots.txt को सीधे इंटरनेट पर दिखाने वाला जादुई फ़ंक्शन
def robots_txt_view(request):
    robots_content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Sitemap: https://fixmyhomes.in/sitemap.xml\n"
    )
    return HttpResponse(robots_content, content_type="text/plain")

urlpatterns = [
    # 1. डैंगो का मुख्य एडमिन पैनल
    path('admin/', admin.site.urls),
    
    # 2. आपके leads ऐप की सभी मुख्य यूआरएल सेटिंग्स
    path('', lead_collection_view, name='lead_form'),
    path('pincodes/', pincodes_view, name='pincodes'),  # यह URL पिनकोड्स पेज के लिए है
    path('statistics/', statistics_view, name='statistics'),  # यह URL स्टेटिस्टिक्स पेज के लिए है
    path('about/', about_view, name='about'),  # यह URL एबाउट पेज के लिए है
    
    # 3. 🎯 आपका नया डिजिटल विजिटिंग कार्ड/पोस्टर पेज (जैसे: https://fixmyhomes.in/card/)
    path('card/', business_card_view, name='business_card'),
    
    # 4. 🎯 गूगल सर्च क्रॉलर के लिए साइटमैप यूआरएल (sitemap.xml)
    path(
        'sitemap.xml', 
        sitemap, 
        {'sitemaps': sitemaps}, 
        name='django.contrib.sitemaps.views.sitemap'
    ),
    
    # 5. 🤖 गूगल बॉट्स के निर्देशों के लिए robots.txt (बिना टेम्पलेट के सीधा सुरक्षित रिस्पॉन्स)
    path('robots.txt', robots_txt_view),
]