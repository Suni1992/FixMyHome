from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    """
    🎯 गूगल क्रॉलर्स को आपकी वेबसाइट के सभी मुख्य पेजों का रास्ता दिखाने वाला साइटमैप क्लास
    """
    changefreq = "weekly"  # यह बताता है कि आपके पेजेस हर हफ्ते अपडेट होते हैं
    priority = 0.8         # सर्च इंजन रैंकिंग के लिए महत्व (0.0 से 1.0)

    def items(self):
        # 🎯 यहाँ आपके urls.py में जो 'name=' पैरामीटर दिए गए हैं, वे सटीक होने चाहिए
        return ['lead_form', 'pincodes', 'statistics', 'about']

    def location(self, item):
        return reverse(item)