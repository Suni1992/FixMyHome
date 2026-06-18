from django.db import models

class Lead(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    service_type = models.CharField(max_length=50, blank=True, null=True) # नई फील्ड जुड़ी
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.name} - {self.area}"