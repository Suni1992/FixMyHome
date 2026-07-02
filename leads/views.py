import os
import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from .models import Lead
from django.db.models import Count
from collections import defaultdict

# 📞 वर्कर के फोन नंबर्स का ग्लोबल मैप (WhatsApp Dispatch के लिए)
WORKER_PHONES = {
    'Ravi Kumar': '919198391632',
    'Amit Sharma': '919198391632',
    'Vikash Prajapati': '919198391632',
    'Sandeep Yadav': '919198391632',
}

# 1. यह फंक्शन मुख्य लीड फॉर्म पेज को हैंडल करता है
def lead_collection_view(request):
    json_path = os.path.join(settings.BASE_DIR, 'pincodes.json')
    pincodes_list = []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
            seen_combinations = set()
            for item in raw_data:
                if 'code' in item and 'area' in item:
                    pincode = str(item['code']).strip()
                    area_name = str(item['area']).strip()
                    combo = f"{pincode}-{area_name.lower()}"
                    
                    if combo not in seen_combinations:
                        pincodes_list.append({
                            'code': pincode,
                            'area': area_name
                        })
                        seen_combinations.add(combo)
            
    except FileNotFoundError:
        pincodes_list = []

    selected_area = request.GET.get('area', '') 
    
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        area = request.POST.get('area')
        service_type = request.POST.get('service_type')
        requirements = request.POST.get('requirements')
        address = request.POST.get('address')
        
        new_lead = Lead(
            name=name, 
            phone=phone, 
            email=email, 
            area=area, 
            service_type=service_type,
            requirements=requirements,
            address=address
        )
        new_lead.save()

        messages.success(request, "धन्यवाद! आपकी लीड सफलतापूर्वक दर्ज कर ली गई है।")
        return redirect('/')

    context = {
        'pincodes': pincodes_list,
        'selected_area': selected_area
    }
    return render(request, 'leads/lead_form.html', context)


# 2. यह फंक्शन पिनकोड्स वाले कार्ड पेज को दिखाता है और रियल-टाइम काउंट करता है
def pincodes_view(request):
    json_path = os.path.join(settings.BASE_DIR, 'pincodes.json')
    pincodes_list = []
    
    lead_counts = defaultdict(int)
    lead_latest = defaultdict(str)
    
    all_leads = Lead.objects.all().order_by('-id')
    
    for lead in all_leads:
        if lead.area:
            area_key = lead.area.strip().lower()
            lead_counts[area_key] += 1
            if area_key not in lead_latest:
                lead_latest[area_key] = lead.id

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
            seen_combinations = set()
            for item in raw_data:
                if 'code' in item and 'area' in item:
                    pincode = str(item['code']).strip()
                    area_name = str(item['area']).strip()
                    combo = f"{pincode}-{area_name.lower()}"
                    
                    if combo not in seen_combinations:
                        format_1 = f"{area_name} ({pincode})".lower()
                        format_2 = f"{pincode} ({area_name})".lower()
                        format_3 = f"{pincode}".lower()
                        
                        total_leads = (lead_counts.get(format_1, 0) + 
                                       lead_counts.get(format_2, 0) + 
                                       lead_counts.get(format_3, 0) +
                                       lead_counts.get(area_name.lower(), 0))
                        
                        sort_rank = max(
                            lead_latest.get(format_1, 0),
                            lead_latest.get(format_2, 0),
                            lead_latest.get(format_3, 0),
                            lead_latest.get(area_name.lower(), 0)
                        )
                        
                        pincodes_list.append({
                            'code': pincode,
                            'area': area_name,
                            'lead_count': total_leads,
                            'sort_rank': sort_rank
                        })
                        seen_combinations.add(combo)
                        
    except FileNotFoundError:
        pincodes_list = []

    pincodes_list.sort(key=lambda x: x['sort_rank'], reverse=True)

    context = {
        'pincodes': pincodes_list
    }
    return render(request, 'leads/pincodes.html', context)


# 3. यह फंक्शन statistics.html पेज को लोड करेगा
def statistics_view(request):
    pin_counts = defaultdict(int)
    service_counts = defaultdict(int)
    
    all_leads = Lead.objects.all()
    
    for lead in all_leads:
        if lead.area:
            match = re.search(r'\b\d{6}\b', lead.area)
            if match:
                pin_counts[match.group()] += 1
            else:
                pin_counts[lead.area.strip()] += 1
                
        if lead.service_type:
            service_key = lead.service_type.strip().capitalize()
            service_counts[service_key] += 1

    sorted_pins = sorted(pin_counts.items(), key=lambda x: x[1], reverse=True)[:6]
    pin_labels = [x[0] for x in sorted_pins]
    pin_data = [x[1] for x in sorted_pins]
    
    if not pin_labels:
        pin_labels = ["No Data"]
        pin_data = [0]

    service_labels = list(service_counts.keys())
    service_data = list(service_counts.values())
    
    if not service_labels:
        service_labels = ["No Data"]
        service_data = [0]

    context = {
        'pin_labels': json.dumps(pin_labels),
        'pin_data': json.dumps(pin_data),
        'service_labels': json.dumps(service_labels),
        'service_data': json.dumps(service_data),
    }
    return render(request, 'leads/statistics.html', context)


# 4. यह फंक्शन about.html पेज को लोड करेगा
def about_view(request):
    return render(request, 'leads/about.html')


# 5. 🎯 वर्कर के लिए डायनेमिक डिजिटल जॉब कार्ड (Saves with lead_id parameter)
def worker_card_view(request, lead_id):
    lead_obj = get_object_or_404(Lead, id=lead_id)
    context = {
        'lead': lead_obj,
        'role': 'worker',
    }
    return render(request, 'leads/business_card.html', context)


# 6. 🎯 ग्राहक के लिए डायनेमिक डिजिटल बुकिंग स्टेटस कार्ड (Saves with lead_id parameter)
def customer_card_view(request, lead_id):
    lead_obj = get_object_or_404(Lead, id=lead_id)
    worker_name = lead_obj.assigned_to
    worker_phone = WORKER_PHONES.get(worker_name, '') if worker_name else ''
    
    context = {
        'lead': lead_obj,
        'role': 'customer',
        'worker_phone': worker_phone
    }
    return render(request, 'leads/business_card.html', context)