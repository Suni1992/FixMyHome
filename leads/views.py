from django.shortcuts import render
from .models import Lead

def lead_collection_view(request):
    context = {'success': False}
    
    if request.method == "POST":
        # फॉर्म से डेटा निकालना
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        area = request.POST.get('area')
        
        # डेटाबेस में सेव करना
        new_lead = Lead(name=name, phone=phone, email=email, area=area)
        new_lead.save()
        
        context['success'] = True # यूज़र को सक्सेस मैसेज दिखाने के लिए
        
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