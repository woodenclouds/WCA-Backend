from django.contrib import admin
from .models import *
# Register your models here.

class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "payment_id", "amount", "user","method")
    list_filter = ("payment_id", "amount", "date_added", "date_updated","user","method")
    search_fields = ("amount","payment_id","method")
   
admin.site.register(Payment_details, PaymentAdmin)