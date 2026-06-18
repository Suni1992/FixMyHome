from django.contrib import admin
from .models import Lead

class LeadAdmin(admin.ModelAdmin):
    # यह आपके एडमिन पैनल को डेटाफ़्रेम/टेबल स्ट्रक्चर में बदल देगा
    list_display = ('name', 'phone', 'email', 'area', 'service_type', 'created_at')

admin.site.register(Lead, LeadAdmin)