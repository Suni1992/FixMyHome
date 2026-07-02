import csv
import urllib.parse
from django.http import HttpResponse
from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe  # 🎯 एरर दूर करने के लिए नया इम्पोर्ट
from .models import Lead

# 📞 अपने चारों वर्कर्स के व्हाट्सएप नंबर्स यहाँ बदलें (कंट्री कोड 91 के साथ बिना स्पेस के लिखें):
WORKER_PHONES = {
    'Ravi Kumar': '919198391632',        # रवि कुमार (Plumbing) का व्हाट्सएप नंबर
    'Amit Sharma': '919198391632',       # अमित शर्मा (Electrical) का व्हाट्सएप नंबर
    'Vikash Prajapati': '919198391632',  # विकाश प्रजापति (Electronics) का व्हाट्सएप नंबर
    'Sandeep Yadav': '919198391632',     # संदीप यादव (Home Appliances) का व्हाट्सएप नंबर
}

# 🛠️ फोन नंबर को व्हाट्सएप के अनुकूल क्लीन करने का सहायक फ़ंक्शन
def clean_phone(phone_str):
    cleaned = "".join(filter(str.isdigit, str(phone_str)))
    if len(cleaned) == 10:
        return "91" + cleaned
    return cleaned

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
    # 🎯 1. फ्रंट पैनल में दिखाए जाने वाले सभी कॉलम्स (बटन जोड़ने के लिए लिस्ट में शामिल किया गया है)
    list_display = (
        'id', 
        'name', 
        'phone', 
        'service_type', 
        'area', 
        'assigned_to', 
        'current_stage', 
        'whatsapp_customer',  # 🔵 कस्टमर व्हाट्सएप बटन
        'whatsapp_worker',    # 🟢 वर्कर व्हाट्सएप बटन
        'amount_total', 
        'amount_paid_status'
    )
    
    # ⚡ 2. जादुई इनलाइन एडिटिंग (लिस्ट स्क्रीन से ही एडिट और सेव करें!)
    list_editable = (
        'assigned_to', 
        'current_stage', 
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

    # 🔵 6. कस्टमर को कार्ड 4 भेजने वाला ऑटोमेटेड बटन
    def whatsapp_customer(self, obj):
        if not obj.phone:
            return "-"
        
        phone = clean_phone(obj.phone)
        msg = (
            f"🙏 *FixMyHome Gorakhpur में आपका स्वागत है!*\n\n"
            f"नमस्ते *{obj.name}*,\n"
            f"FixMyHome पर अपनी लीड दर्ज कराने के लिए आपका धन्यवाद।\n\n"
            f"हमें आपकी रिक्वेस्ट मिल गई है:\n"
            f"🛠️ *सर्विस:* {obj.service_type or 'Home Service'}\n"
            f"📍 *एरिया:* {obj.area or 'Gorakhpur'}\n\n"
            f"हमारा एक्सपर्ट इंजीनियर/वर्कर अगले *30 मिनट* के अंदर आपसे संपर्क करेगा और काम का समय तय करेगा।\n\n"
            f"📞 किसी भी सहायता के लिए हमें सीधे संपर्क करें: *+91 91983 91632*\n"
            f"🌐 हमारी वेबसाइट: https://fixmyhomes.in"
        )
        encoded_msg = urllib.parse.quote(msg)
        url = f"https://wa.me/{phone}?text={encoded_msg}"
        return format_html(
            '<a class="button" style="background-color: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: bold;" href="{}" target="_blank">📲 Msg Customer</a>', 
            url
        )
    whatsapp_customer.short_description = 'Customer Msg'

    # 🟢 7. वर्कर को कार्ड 3 (जॉब असाइनमेंट) भेजने वाला ऑटोमेटेड बटन
    def whatsapp_worker(self, obj):
        # ⚠️ एरर को ठीक करने के लिए format_html की जगह mark_safe का इस्तेमाल किया गया है
        if not obj.assigned_to:
            return mark_safe('<span style="color: #94a3b8; font-size: 11px;">Not Assigned</span>')
        
        worker_phone = WORKER_PHONES.get(obj.assigned_to)
        if not worker_phone:
            return mark_safe('<span style="color: #ef4444; font-size: 11px;">No Phone Saved</span>')
        
        address_str = getattr(obj, 'address', '') or 'पता नहीं लिखा गया'
        req_str = obj.requirements or 'कोई विशेष समस्या नहीं लिखी गई'
        
        msg = (
            f"🚨 *NEW JOB ASSIGNED - FIXMYHOME* 🚨\n\n"
            f"नमस्ते टीम, आपको एक नया काम असाइन किया गया है। कृपया ग्राहक से तुरंत संपर्क करें:\n\n"
            f"👤 *ग्राहक का नाम:* {obj.name}\n"
            f"📞 *मोबाइल नंबर:* {obj.phone}\n"
            f"📍 *इलाका / पिन कोड:* {obj.area}\n"
            f"🏠 *पूरा पता:* {address_str}\n\n"
            f"🛠️ *काम का प्रकार (Service):* {obj.service_type}\n"
            f"📝 *ग्राहक की आवश्यकता (Details):* {req_str}\n\n"
            f"💰 *तय की गई कुल रकम:* ₹{obj.amount_total}\n"
            f"📊 *पेमेंट स्टेटस:* {obj.get_amount_paid_status_display()}\n\n"
            f"_नोट: काम पूरा होने के बाद एडमिन को तुरंत सूचित करें और फोटो भेजें।_"
        )
        encoded_msg = urllib.parse.quote(msg)
        url = f"https://wa.me/{worker_phone}?text={encoded_msg}"
        return format_html(
            '<a class="button" style="background-color: #10b981; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: bold;" href="{}" target="_blank">🟢 Send to Worker</a>', 
            url
        )
    whatsapp_worker.short_description = 'Worker Msg'
    
    # 📊 8. डैशबोर्ड कार्ड्स के लिए लाइव कैलकुलेशन डेटा पास करना
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