import csv
from django.http import HttpResponse
from django.contrib import admin
from django.db import models
from .models import Lead

# 🎯 Selected Leads को Excel / CSV में डाउनलोड करने का जादुई एक्शन
@admin.action(description="Selected Leads को CSV (Excel) में डाउनलोड करें")
def export_leads_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="fixmyhome_leads.csv"'
    
    writer = csv.writer(response)
    
    # 📋 एक्सेल की हेडिंग्स
    writer.writerow([
        'Lead ID', 
        'Customer Name', 
        'Phone Number', 
        'Email Address', 
        'Area / Pin Code', 
        'Service Type', 
        'Full Address', 
        'Assigned To',
        'Current Stage',
        'Engineer Status',
        'Amount Paid Status',
        'Amount Total',
        'Requirements'
    ])
    
    # 📥 डेटाबेस से डेटा निकालकर लिखना
    for lead in queryset:
        writer.writerow([
            lead.id,
            lead.name,
            lead.phone,
            lead.email,
            lead.area,
            lead.service_type,
            getattr(lead, 'address', ''),
            lead.get_assigned_to_display() if lead.assigned_to else 'Not Assigned',
            lead.get_current_stage_display(),
            lead.engineer_status or '',
            lead.get_amount_paid_status_display(),
            lead.amount_total,
            lead.requirements
        ])
        
    return response

# ⚙️ Django Admin में Leads को रजिस्टर करना और कस्टमाइज़ करना
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    # 🎯 1. फ्रंट पैनल में दिखाए जाने वाले सभी कॉलम्स (ताकि सब कुछ स्क्रीन पर ही दिख जाए)
    list_display = (
        'id', 
        'name', 
        'phone', 
        'service_type', 
        'area', 
        'assigned_to', 
        'current_stage', 
        'engineer_status', 
        'amount_total', 
        'amount_paid_status'
    )
    
    # ⚡ 2. जादुई इनलाइन एडिटिंग (बिना लीड खोले सीधे लिस्ट स्क्रीन से ही एडिट और सेव करें!)
    list_editable = (
        'assigned_to', 
        'current_stage', 
        'engineer_status', 
        'amount_total', 
        'amount_paid_status'
    )
    
    # 🔍 3. दाईं तरफ के बेहतरीन फ़िल्टर्स
    list_filter = (
        'current_stage', 
        'assigned_to', 
        'amount_paid_status', 
        'service_type', 
        'created_at'
    )
    
    # 🔎 4. सर्च करने के लिए एडवांस्ड कीवर्ड्स
    search_fields = (
        'name', 
        'phone', 
        'area', 
        'address', 
        'engineer_status', 
        'assigned_to'
    )
    
    # 📥 5. एक्सपोर्ट एक्शन जोड़ना
    actions = [export_leads_to_csv]
    
    # 📊 6. डैशबोर्ड कार्ड्स के लिए लाइव कैलकुलेशन डेटा पास करना
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # सभी लीड्स का लाइव काउंट
        leads_qs = Lead.objects.all()
        total_leads = leads_qs.count()
        
        # एक्टिव और कम्पलीटेड लीड्स
        active_leads = leads_qs.exclude(current_stage__in=['completed', 'cancelled']).count()
        completed_leads = leads_qs.filter(current_stage='completed').count()
        
        # कुल कलेक्टेड रेवेन्यू और पेंडिंग रेवेन्यू कैलकुलेशन
        collected_rev = leads_qs.filter(amount_paid_status='paid').aggregate(models.Sum('amount_total'))['amount_total__sum'] or 0
        partially_paid_rev = leads_qs.filter(amount_paid_status='partially_paid').aggregate(models.Sum('amount_total'))['amount_total__sum'] or 0
        
        # हाफ पेमेंट को भी रेवेन्यू में जोड़ना
        total_collected = float(collected_rev) + (float(partially_paid_rev) * 0.5)
        total_pending = float(leads_qs.filter(amount_paid_status='unpaid').aggregate(models.Sum('amount_total'))['amount_total__sum'] or 0) + (float(partially_paid_rev) * 0.5)
        
        extra_context['dashboard_stats'] = {
            'total': total_leads,
            'active': active_leads,
            'completed': completed_leads,
            'collected': round(total_collected, 2),
            'pending': round(total_pending, 2),
        }
        
        return super().changelist_view(request, extra_context=extra_context)