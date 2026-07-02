import csv
import urllib.parse
from django.http import HttpResponse
from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Lead

# 📞 अपने चारों वर्कर्स के व्हाट्सएप नंबर्स यहाँ बदलें
WORKER_PHONES = {
    'Ravi Kumar': '919198391632',
    'Amit Sharma': '919198391632',
    'Vikash Prajapati': '919198391632',
    'Sandeep Yadav': '919198391632',
}

# 🛠️ फोन नंबर क्लीन करने का सहायक फ़ंक्शन
def clean_phone(phone_str):
    cleaned = "".join(filter(str.isdigit, str(phone_str)))
    if len(cleaned) == 10:
        return "91" + cleaned
    return cleaned

@admin.action(description="Selected Leads को CSV (Excel) में डाउनलोड करें")
def export_leads_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="fixmyhome_leads.csv"'
    writer = csv.writer(response)
    
    writer.writerow([
        'Lead ID', 'Customer Name', 'Phone Number', 'Email Address', 
        'Area / Pin Code', 'Service Type', 'Full Address', 'Assigned To',
        'Current Stage', 'Engineer Status', 'Amount Paid Status', 'Amount Total', 'Requirements'
    ])
    
    for lead in queryset:
        writer.writerow([
            lead.id, lead.name, lead.phone, lead.email, lead.area, lead.service_type,
            getattr(lead, 'address', ''), lead.get_assigned_to_display() if lead.assigned_to else 'Not Assigned',
            lead.get_current_stage_display(), lead.engineer_status or '', lead.get_amount_paid_status_display(),
            lead.amount_total, lead.requirements
        ])
    return response

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'phone', 'service_type', 'area', 'assigned_to', 
        'current_stage', 'whatsapp_customer', 'whatsapp_worker', 
        'amount_total', 'amount_paid_status'
    )
    
    list_editable = (
        'assigned_to', 'current_stage', 'amount_total', 'amount_paid_status'
    )
    
    list_filter = (
        'current_stage', 'assigned_to', 'amount_paid_status', 'service_type', 'created_at'
    )
    
    search_fields = (
        'name', 'phone', 'area', 'address', 'engineer_status', 'assigned_to'
    )
    
    actions = [export_leads_to_csv]

    # 🔵 ग्राहक को लाइव कन्फर्मेशन कार्ड भेजने वाला ऑटोमेटेड बटन
    def whatsapp_customer(self, obj):
        if not obj.phone:
            return "-"
        
        phone = clean_phone(obj.phone)
        # 🔗 इस ग्राहक का लाइव बुकिंग स्टेटस कार्ड लिंक
        live_card_url = f"https://fixmyhomes.in/card/customer/{obj.id}/"
        
        msg = (
            f"> \U0001F197 *FIXMYHOME GORAKHPUR*\n"
            f"> ────────────────────────\n"
            f"> नमस्ते *{obj.name}*,\n"
            f"> FixMyHome पर अपनी लीड दर्ज कराने के लिए आपका धन्यवाद।\n"
            f"> ────────────────────────\n"
            f"> \U0001F6E0 *सर्विस:* {obj.service_type or 'Home Service'}\n"
            f"> \U0001F4CD *एरिया:* {obj.area or 'Gorakhpur'}\n"
            f"> ────────────────────────\n"
            f"> \U0001F4F1 *लाइव बुकिंग स्टेटस और कार्ड देखें:*\n"
            f"> {live_card_url}\n"
            f"> ────────────────────────\n"
            f"> हमारा एक्सपर्ट इंजीनियर/वर्कर अगले *30 मिनट* के अंदर आपसे संपर्क करेगा।\n\n"
            f"📞 *हेल्पलाइन:* +91 91983 91632\n"
            f"🌐 *वेबसाइट:* https://fixmyhomes.in"
        )
        encoded_msg = urllib.parse.quote(msg)
        url = f"https://wa.me/{phone}?text={encoded_msg}"
        return format_html(
            '<a class="button" style="background-color: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: bold;" href="{}" target="_blank">📲 Msg Customer</a>', 
            url
        )
    whatsapp_customer.short_description = 'Customer Msg'

    # 🟢 वर्कर को लाइव जॉब असाइनमेंट कार्ड भेजने वाला ऑटोमेटेड बटन
    def whatsapp_worker(self, obj):
        if not obj.assigned_to:
            return mark_safe('<span style="color: #94a3b8; font-size: 11px;">Not Assigned</span>')
        
        worker_phone = WORKER_PHONES.get(obj.assigned_to)
        if not worker_phone:
            return mark_safe('<span style="color: #ef4444; font-size: 11px;">No Phone Saved</span>')
        
        address_str = getattr(obj, 'address', '') or 'पता नहीं लिखा गया'
        # 🔗 इस काम का लाइव वर्कर जॉब कार्ड लिंक
        live_card_url = f"https://fixmyhomes.in/card/worker/{obj.id}/"
        
        msg = (
            f"> \U0001F7E9 *NEW JOB ASSIGNED - FIXMYHOME*\n"
            f"> ────────────────────────\n"
            f"> नमस्ते टीम, आपको एक नया काम असाइन किया गया है। कृपया ग्राहक से तुरंत संपर्क करें:\n\n"
            f"> \U0001F464 *ग्राहक का नाम:* {obj.name}\n"
            f"> \U0001F4CD *इलाका / पिन कोड:* {obj.area}\n"
            f"> \U0001F6E0 *काम का प्रकार (Service):* {obj.service_type}\n"
            f"> ────────────────────────\n"
            f font-weight: bold;> \U0001F4F1 *पूरा पता, नंबर और जॉब कार्ड देखने के लिए इस लिंक को खोलें:*\n"
            f"> {live_card_url}\n"
            f"> ────────────────────────\n"
            f"> _नोट: काम पूरा होने के बाद एडमिन को तुरंत सूचित करें और फोटो भेजें।_"
        )
        encoded_msg = urllib.parse.quote(msg)
        url = f"https://wa.me/{worker_phone}?text={encoded_msg}"
        return format_html(
            '<a class="button" style="background-color: #10b981; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: bold;" href="{}" target="_blank">🟢 Send to Worker</a>', 
            url
        )
    whatsapp_worker.short_description = 'Worker Msg'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        leads_qs = Lead.objects.all()
        total_leads = leads_qs.count()
        
        active_leads = leads_qs.exclude(current_stage__in=['completed', 'cancelled']).count()
        completed_leads = leads_qs.filter(current_stage='completed').count()
        
        collected_rev = leads_qs.filter(amount_paid_status='paid').aggregate(models.Sum('amount_total'))['amount_total__sum'] or 0
        partially_paid_rev = leads_qs.filter(amount_paid_status='partially_paid').aggregate(models.Sum('amount_total'))['amount_total__sum'] or 0
        
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