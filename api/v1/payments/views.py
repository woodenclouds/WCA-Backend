import traceback
import logging
import json
from django.utils import timezone
from datetime import timedelta

from datetime import date

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#email
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

from api.v1.accounts.serializers import *
from accounts.models import *
from general.models import *
from payments.models import *
# from payments.models import *
# from general.decorators import group_required
from general.functions import *
from general.encryptions import *
from api.v1.accounts.functions import *
from . functions import *
from .serializers import *
from .razorpay.main import *

rz_client=RazorPayClient()

@api_view(['POST'])
@permission_classes([AllowAny])
def transaction_view(request):
    user = request.user
    try: 
        serialized =  TransactionModelSerializer(data=request.data)
        
        if serialized.is_valid():
            order_id = request.data["order_id"]
            payment_id = request.data["payment_id"]
            signature = request.data["signature"]
            amount = request.data["amount"]
            
            # Verify the payment
            rz_client.verify_payment(
                razorpay_order_id=order_id,
                razorpay_payment_id=payment_id,
                razorpay_signature=signature
            )
            
            # Fetch payment details
            payment_details = rz_client.get_payment_details(payment_id)
            print("Payment details:", payment_details)
            
           # Extract the necessary details for storing
            method = payment_details.get('method')
            print("method",method)
            card_last_four = None
            bank = None
            vpa = None
            upi_transaction_id = None

            if method == 'card':
                card_last_four = payment_details.get('card', {}).get('last4')
            elif method == 'netbanking':
                bank = payment_details.get('bank')
            elif method == 'upi':
                vpa = payment_details.get('vpa') or payment_details.get('upi', {}).get('vpa')
                upi_transaction_id = payment_details.get('acquirer_data', {}).get('upi_transaction_id')
            

            print(f"card 4 {card_last_four} bank {bank} vpa {vpa} upi transaction id  {upi_transaction_id}")

            # Create new payment entry
            new_payment = Payment_details.objects.create(
                payment_id=payment_id,
                order_id=order_id,
                signature=signature,  
                amount=amount,
                method=method,
                card_last_four=card_last_four,
                bank=bank,
                vpa=vpa,
                user=user,
                upi_transaction_id=upi_transaction_id
            )

            new_payment.save()

            response_data = {
                "StatusCode": 6000,
                "data": {
                    "title": "Success",
                    "message": "Payment Created",
                    "data": {
                        "payment_id": new_payment.id,
                }
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data":{
                    "title": "Error",
                    "message":generate_serializer_errors(serialized.errors)
                } 
            }
    except Exception as E:
        transaction.rollback()
        errType = E.__class__.__name__
        errors = {
            errType: traceback.format_exc()
        }
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(E),
            "response": errors
        }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_order(request):
    try: 
        serialized =  CreateOrderSerializer(data=request.data)
        
        if serialized.is_valid():
            order_response = rz_client.create_order(
            amount=serialized.validated_data.get("amount"),
            currency=serialized.validated_data.get("currency")
        )


            response_data = {
                "StatusCode": 6000,
                "data": {
                    "title": "Success",
                    "message": "order created",
                    "data": order_response
                }
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data":{
                    "title": "Error",
                    "message":generate_serializer_errors(serialized.errors)
                } 
            }
    except Exception as E:
        transaction.rollback()
        errType = E.__class__.__name__
        errors = {
            errType: traceback.format_exc()
        }
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "api": request.get_full_path(),
            "request": request.data,
            "message": str(E),
            "response": errors
        }

    return Response(response_data, status=status.HTTP_200_OK)