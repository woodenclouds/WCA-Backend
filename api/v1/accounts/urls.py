from django.urls import re_path, path
from .  import  views

app_name = 'api_v1_accounts'

urlpatterns = [

re_path(r'^user/signup/$', views.user_signup, name="user-signup"),
re_path(r'^user/verify/$', views.verify_otp, name="user_verify"),
re_path(r'^user/login/$', views.user_login, name="user_login"),
re_path(r'^user/login-verify/$', views.user_login_verify, name="user_login_verify"),
re_path(r'^user/profile-view/$', views.view_user_profile, name="user_profile_view"),
re_path(r'^user/edit-profile/$', views.edit_user_profile, name="user_edit_profile"),
   
    

]