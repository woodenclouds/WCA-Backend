from django.urls import re_path, path
from .  import  views

app_name = 'api_v1_payments'

urlpatterns = [
 

    re_path(r'^user/order/create/$', views.create_order, name="user-create-order"),
    re_path(r'^user/order/complete/$', views.transaction_view, name="user-complete-order"),


    

]