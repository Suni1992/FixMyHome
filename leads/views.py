import os
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import Lead
from django.db.models import Count
from collections import defaultdict

# 1. यह फंक्शन मुख्य लीड फॉर्म पेज को हैंडल करता है
def lead_collection_view(request):
    json_path = os.path.join(settings.BASE_DIR, 'pincodes.json')
    pincodes_list = []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
            # --- लूप: एक पिनकोड के सभी यूनीक इलाकों को फिल्टर करना ---
            seen_combinations = set()
            for item in raw_data:
                if 'code' in item and 'area' in item:
                    # फालतू स्पेस हटाकर यूनीक चाबी बनाई
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
    
    # जब यूजर फॉर्म सबमिट करेगा (POST)
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        area = request.POST.get('area')
        service_type = request.POST.get('service_type')
        requirements = request.POST.get('requirements')
        address = request.POST.get('address') # 📍 नए एड्रेस फ़ील्ड की वैल्यू उठाना
        
        # नया ऑब्जेक्ट क्रिएट करके डेटाबेस में सेव करना (requirements और address के साथ)
        new_lead = Lead(
            name=name, 
            phone=phone, 
            email=email, 
            area=area, 
            service_type=service_type,
            requirements=requirements,
            address=address # 📍 मॉडल में सेव करना
        )
        new_lead.save()

        # 🎯 यहाँ हमने सक्सेस मैसेज बना दिया जो HTML के {% if messages %} को दिखाई देगा
        messages.success(request, "धन्यवाद! आपकी लीड सफलतापूर्वक दर्ज कर ली गई है।")

        # डैंगो मैसेजेस के साथ रीडायरेक्ट करना बेस्ट प्रैक्टिस है ताकि पेज रिफ्रेश (F5) करने पर दोबारा फॉर्म सबमिट न हो (No duplicate submission)
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
    
    # डेटाबेस से हरिया की असली लीड्स की गिनती निकालना
    lead_counts = defaultdict(int)
    lead_latest = defaultdict(str)  # नई लीड को ट्रैक करने के लिए
    
    all_leads = Lead.objects.all().order_by('-id')  # नई लीड्स पहले मिलेंगी
    
    for lead in all_leads:
        if lead.area:
            area_key = lead.area.strip().lower()
            lead_counts[area_key] += 1
            if area_key not in lead_latest:
                lead_latest[area_key] = lead.id  # सबसे नई लीड की आईडी स्टोर की

    # JSON फ़ाइल से डेटा लोड करना
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
                        # 🎯 डेटाबेस में पुराने और नए सभी फॉर्मेट्स को मैच करना:
                        format_1 = f"{area_name} ({pincode})".lower() # एक्जाम्पल: badago (273213)
                        format_2 = f"{pincode} ({area_name})".lower() # एक्जाम्पल: 273002 (a.p.station)
                        format_3 = f"{pincode}".lower()               # सिर्फ पिनकोड: 273016
                        
                        # तीनों फॉर्मेट्स और डायरेक्ट नाम के काउंट को आपस में जोड़ा
                        total_leads = (lead_counts.get(format_1, 0) + 
                                       lead_counts.get(format_2, 0) + 
                                       lead_counts.get(format_3, 0) +
                                       lead_counts.get(area_name.lower(), 0))
                        
                        # सॉर्टिंग रैंक ढूंढना
                        sort_rank = max(
                            lead_latest.get(format_1, 0),
                            lead_latest.get(format_2, 0),
                            lead_latest.get(format_3, 0),
                            lead_latest.get(area_name.lower(), 0)
                        )
                        
                        pincodes_list.append({
                            'code': pincode,
                            'area': area_name,
                            'lead_count': total_leads,  # एकदम असली रियल-टाइम काउंट
                            'sort_rank': sort_rank
                        })
                        seen_combinations.add(combo)
                        
    except FileNotFoundError:
        pincodes_list = []

    # 3. सॉर्टिंग: जिस एरिया में नई लीड आएगी (बड़ी ID), वह सबसे ऊपर दिखेगा
    pincodes_list.sort(key=lambda x: x['sort_rank'], reverse=True)

    context = {
        'pincodes': pincodes_list
    }
    return render(request, 'leads/pincodes.html', context)


# 3. यह फंक्शन statistics.html पेज को लोड करेगा
def statistics_view(request):
    # 1. डेटाबेस से पिनकोड के हिसाब से असली लीड्स का काउंट निकालना
    # (चूँकि डेटाबेस में "Golghar (273001)" या "273002 (A.P.station)" सेव है, हम उसमें से पिनकोड नंबर निकालेंगे)
    pin_counts = defaultdict(int)
    # 2. सर्विस टाइप के हिसाब से काउंट निकालना
    service_counts = defaultdict(int)
    
    all_leads = Lead.objects.all()
    
    for lead in all_leads:
        # पिनकोड काउंट करने का लॉजिक
        if lead.area:
            # टेक्स्ट में से 6 अंकों का पिनकोड ढूंढना (जैसे 273001)
            import re
            match = re.search(r'\b\d{6}\b', lead.area)
            if match:
                pin_counts[match.group()] += 1
            else:
                # अगर सिर्फ नाम सेव है, तो उसे क्लीन करके डाल दें
                pin_counts[lead.area.strip()] += 1
                
        # सर्विस टाइप काउंट करने का लॉजिक
        if lead.service_type:
            service_key = lead.service_type.strip().capitalize()
            service_counts[service_key] += 1

    # चार्ट्स के लिए लिस्ट तैयार करना (ताकि जावास्क्रिप्ट समझ सके)
    # टॉप 6 पिनकोड्स
    sorted_pins = sorted(pin_counts.items(), key=lambda x: x[1], reverse=True)[:6]
    pin_labels = [x[0] for x in sorted_pins]
    pin_data = [x[1] for x in sorted_pins]
    
    # अगर कोई डेटा न हो तो डिफॉल्ट दिखाने के लिए खाली लिस्ट न भेजें
    if not pin_labels:
        pin_labels = ["No Data"]
        pin_data = [0]

    # सारी सर्विसेज का डेटा
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


# 5. 🎯 यह फंक्शन आपके डिजिटल विजिटिंग कार्ड (Poster) को लोड करेगा
def business_card_view(request):
    return render(request, 'leads/business_card.html')