from django.contrib import admin
from django.urls import path
from leads.views import lead_collection_view,pincodes_view, statistics_view,about_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lead_collection_view, name='lead_form'),
    path('pincodes/', pincodes_view, name='pincodes'),  # यह URL पिनकोड्स पेज के लिए है
    path('statistics/', statistics_view, name='statistics'),  # यह URL स्टेटिस्टिक्स पेज के लिए है
    path('about/', about_view, name='about'),  # यह URL एबाउट पेज के लिए है
]
