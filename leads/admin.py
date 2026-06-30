import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import Lead

# 🎯 Selected Leads को Excel / CSV में डाउनलोड करने का जादुई एक्शन
@admin.action(description="Selected Leads को CSV (Excel) में डाउनलोड करें")
def export_leads_to_csv(modeladmin, request, queryset):
    # 'utf-8-sig' एनकोडिंग एक्सेल और गूगल शीट्स में हिंदी और स्पेशल कैरेक्टर्स को बिल्कुल सही दिखाता है
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="fixmyhome_leads.csv"'
    
    writer = csv.writer(response)
    
    # 📋 एक्सेल की हेडिंग्स (Columns)
    writer.writerow([
        'Lead ID', 
        'Customer Name', 
        'Phone Number', 
        'Email Address', 
        'Area / Pin Code', 
        'Service Type', 
        'Full Address', 
        'Requirements'
    ])
    
    # 📥 डेटाबेस से डेटा निकालकर रो (Rows) लिखना
    for lead in queryset:
        writer.writerow([
            lead.id,
            lead.name,
            lead.phone,
            lead.email,
            lead.area,
            lead.service_type,
            getattr(lead, 'address', ''), # 📍 एड्रेस को सुरक्षित रूप से एक्सेल में लिखना
            lead.requirements
        ])
        
    return response

# ⚙️ Django Admin में Leads को रजिस्टर करना और कस्टमाइज़ करना
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    # एडमिन टेबल में कौन-कौन से कॉलम्स दिखेंगे
    list_display = ('id', 'name', 'phone', 'service_type', 'area', 'address')
    
    # दाईं तरफ फ़िल्टर बॉक्स (Service और Area के आधार पर छांटने के लिए)
    list_filter = ('service_type',)
    
    # सर्च करने के लिए बॉक्स (नाम, फ़ोन नंबर, पता या आवश्यकता से सर्च करें)
    search_fields = ('name', 'phone', 'requirements', 'address')
    
    # 🎯 हमारा कस्टम एक्सपोर्ट बटन जोड़ना
    actions = [export_leads_to_csv]