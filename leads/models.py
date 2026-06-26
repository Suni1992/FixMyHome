from django.db import models

class Lead(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    area = models.CharField(max_length=100)
    service_type = models.CharField(max_length=50, blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    STAGE_CHOICES = [
        ('new', 'New Lead'),
        ('assigned', 'Engineer Assigned'),
        ('in_progress', 'Work In Progress'),
        ('completed', 'Work Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Fully Paid'),
    ]

    # 🎯 यहाँ हमने आपके 4 वर्कर्स की ड्रॉपडाउन लिस्ट (Choices) बना दी है
    WORKER_CHOICES = [
        ('Ravi Kumar', 'रवि कुमार (Plumbing)'),
        ('Amit Sharma', 'अमित शर्मा (Electrical)'),
        ('Vikash Prajapati', 'विकाश प्रजापति (Electronics)'),
        ('Sandeep Yadav', 'संदीप यादव (Home Appliances)'),
    ]

    # 🚀 पुरानी assigned_to लाइन को हटाकर यह नई चॉइस वाली लाइन पेस्ट करें
    assigned_to = models.CharField(
        max_length=100, 
        choices=WORKER_CHOICES, 
        blank=True, 
        null=True, 
        help_text="लीड के लिए वर्कर या इंजीनियर चुनें"
    )
    
    current_stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='new')
    engineer_status = models.CharField(max_length=100, blank=True, null=True, help_text="जैसे: On the way, Reached, Delayed")
    amount_paid_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='unpaid')
    amount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="कुल तय रकम")
    customer_review = models.TextField(blank=True, null=True, help_text="काम पूरा होने के बाद कस्टमर का फीडबैक")
    rating = models.IntegerField(blank=True, null=True, help_text="1 से 5 स्टार रेटिंग")

    def __str__(self):
        return f"{self.name} - {self.get_current_stage_display()}"