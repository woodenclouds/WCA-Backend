from rest_framework import serializers

from django.db.models import Sum, Count
from django.db.models import Avg

from accounts.models import *
from general.encryptions import encrypt,decrypt

from datetime import datetime
from . functions import *
from payments.models import *


class CreateOrderSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency=serializers.CharField()


class TransactionModelSerializer(serializers.Serializer):
    class Meta:
        model=Payment_details
        fields = ["payment_id", "order_id", "signature", "amount"]

