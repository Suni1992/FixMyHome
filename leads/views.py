from django.shortcuts import render
from .models import Lead
import os
import json
from django.conf import settings  # यह लाइन बहुत ज़रूरी है क्योंकि नीचे settings.BASE_DIR इस्तेमाल हो रहा है

def lead_collection_view(request):
    json_path = os.path.join(settings.BASE_DIR, 'pincodes.json')
    pincodes_list = []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
            # --- नया लॉजिक: एक पिनकोड के सभी यूनीक इलाकों को आने दें ---
            seen_combinations = set()
            for item in raw_data:
                if 'code' in item and 'area' in item:
                    # हम पिनकोड + इलाका दोनों को मिलाकर एक यूनिक आईडी बना रहे हैं
                    combo = f"{item['code']}-{item['area']}"
                    if combo not in seen_combinations:
                        pincodes_list.append(item)
                        seen_combinations.add(combo)
            # --- नया लॉजिक समाप्त ---
            
    except FileNotFoundError:
        pincodes_list = []

    selected_area = request.GET.get('area', '') 

    context = {
        'success': False,
        'pincodes': pincodes_list,  # अब इसमें एक पिनकोड के सारे अलग-अलग इलाके आ जाएंगे!
        'selected_area': selected_area
    }
    
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        area = request.POST.get('area')

        new_lead = Lead(name=name, phone=phone, email=email, area=area)
        new_lead.save()

        context['success'] = True

    return render(request, 'leads/lead_form.html', context)

# यह फंक्शन pincodes.html पेज को दिखाएगा
def pincodes_view(request):
    return render(request, 'leads/pincodes.html')

# यह फंक्शन statistics.html पेज को लोड करेगा
def statistics_view(request):
    return render(request, 'leads/statistics.html')


# यह फंक्शन about.html पेज को लोड करेगा
def about_view(request):
    return render(request, 'leads/about.html')