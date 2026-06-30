from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    """
    🎯 गूगल क्रॉलर्स को आपकी वेबसाइट के सभी मुख्य पेजों का रास्ता दिखाने वाला साइटमैप क्लास
    """
    changefreq = "weekly"  # यह बताता है कि आपके पेजेस हर हफ्ते अपडेट होते हैं
    priority = 0.8         # सर्च इंजन रैंकिंग के लिए महत्व (0.0 से 1.0)

    def items(self):
        # ये आपके views.py में मौजूद व्यूज के नाम हैं जिन्हें क्रॉल करना है
        return ['lead_collection_view', 'pincodes_view', 'statistics_view', 'about_view']

    def location(self, item):
        return reverse(item)