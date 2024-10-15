from django.urls import re_path, path
from .  import  views

app_name = 'api_v1_activities'

urlpatterns = [


re_path(r'^user/get-webinar-list/$', views.get_webinar_list, name="get_webinar_list"),
re_path(r'^user/purchase-course/$', views.purchase_course, name="purchase_course"),
   
    

]