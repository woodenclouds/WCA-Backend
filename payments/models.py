from django.db import models
from .functions import get_auto_id
from general.models import BaseModel
from accounts.models import User

# Create your models here.
class Payment_details(BaseModel):
    payment_id=models.CharField(max_length=200)
    order_id=models.CharField(max_length=200)
    signature=models.CharField(max_length=200)
    amount=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    method = models.CharField(max_length=50, null=True, blank=True)  # Payment method (e.g., card, upi, netbanking)
    card_last_four = models.CharField(max_length=4, null=True, blank=True)  # Last 4 digits of the card, if card payment
    bank = models.CharField(max_length=100, null=True, blank=True)  # Bank name, if netbanking
    vpa = models.CharField(max_length=100, null=True, blank=True)  # VPA, if UPI payment
    upi_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self._state.adding:
                auto_id = get_auto_id(Payment_details)
                self.auto_id = auto_id

        super(Payment_details, self).save(*args, **kwargs)
    
    class Meta:
        db_table = "payments_payment_details"
        verbose_name = "Payment_details"
        verbose_name_plural = "Payment_details"
        ordering = ("id",)

    def __str__(self):
        return f"{self.payment_id}"