from django.contrib import admin
from .models import Lead

class LeadAdmin(admin.ModelAdmin):
    # 🎯 'get_assigned_to_display' को हमने 'CURRENT STAGE' के ठीक पहले (बगल में) रख दिया है
    list_display = (
        'name', 
        'area', 
        'service_type', 
        'assigned_worker_column',  # 🚀 यह हमारा कस्टमाइज्ड कॉलम है
        'current_stage', 
        'amount_paid_status', 
        'created_at'
    )
    
    list_filter = ('current_stage', 'amount_paid_status', 'service_type', 'created_at')
    search_fields = ('name', 'phone', 'assigned_to', 'area')
    
    fieldsets = (
        ('कस्टमर और सर्विस की जानकारी', {
            'fields': ('name', 'phone', 'email', 'area', 'service_type', 'requirements')
        }),
        ('वर्क और इंजीनियर ट्रैकिंग', {
            'fields': ('assigned_to', 'current_stage', 'engineer_status')
        }),
        ('पेमेंट और हिसाब-किताब', {
            'fields': ('amount_total', 'amount_paid_status')
        }),
        ('फीडबैक और रिव्यूज', {
            'fields': ('customer_review', 'rating')
        }),
    )

    # 🎯 "METHOD" नाम को बदलकर "ASSIGNED WORKER" करने का जादुई फंक्शन
    @admin.display(description='ASSIGNED WORKER', ordering='assigned_to')
    def assigned_worker_column(self, obj):
        return obj.get_assigned_to_display() or '-'

admin.site.register(Lead, LeadAdmin)