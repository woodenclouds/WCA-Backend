from django.forms import ValidationError
from . import client
class RazorPayClient:
    def create_order(self,amount,currency):
        data = {
        "amount": int(amount)*100,
        "currency": "INR",}
        try:
            order=client.order.create(data=data)
            return order
        except Exception as e:
            raise ValidationError(
                {
                    "message":e
                }
            )
    
    def verify_payment(self,razorpay_order_id,razorpay_payment_id,razorpay_signature):
            try:
                print(f" razorpay order={razorpay_order_id},paymentid={razorpay_payment_id},signature={razorpay_signature}")
                #will return true or false
                return client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
                })
            except Exception as e:
                 raise ValidationError(
                {
                    "message":e
                }
            )
    def get_payment_details(self, payment_id):
        try:
            # Fetch payment details using payment_id
            payment_details = client.payment.fetch(payment_id)
            
            return payment_details
        except Exception as e:
            raise ValidationError({"message": str(e)})