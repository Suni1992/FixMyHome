from django.shortcuts import render
from .models import Lead
import os
import json
from django.conf import settings  # यह लाइन बहुत ज़रूरी है क्योंकि नीचे settings.BASE_DIR इस्तेमाल हो रहा है

def lead_collection_view(request):
    # JSON फ़ाइल से पिनकोड लोड करना
    json_path = os.path.join(settings.BASE_DIR, 'pincodes.json')
    pincodes_list = []
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            pincodes_list = json.load(f)
    except FileNotFoundError:
        pincodes_list = []

    # URL से ऑटो-सिलेक्ट के लिए पिनकोड उठाना
    selected_area = request.GET.get('area', '') 

    context = {
        'success': False,
        'pincodes': pincodes_list,
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