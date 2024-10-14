from django.urls import re_path, path
from .  import  views

app_name = 'api_v1_courses'

urlpatterns = [

re_path(r'^user/get-course-list/$', views.get_courses_list, name="get_courses_list"),
   
    

]