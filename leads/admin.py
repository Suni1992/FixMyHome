from django.contrib import admin
from .models import Lead # ध्यान दें: यहाँ अपने Pincode मॉडल का असली नाम लिखें जो models.py में है

admin.site.register(Lead)
