from django.urls import re_path, path
from .  import  views

app_name = 'api_v1_activities'

urlpatterns = [


re_path(r'^user/get-webinar-list/$', views.get_webinar_list, name="get_webinar_list"),
re_path(r'^user/purchase-course/$', views.purchase_course, name="purchase_course"),
re_path(r'^user/update-progress/(?P<pk>.*)/$',views.update_user_progress,name="update_user_progress"),
re_path(r'^user/complete-chapter-progress/(?P<pk>.*)/$',views.user_complete_chapter_progress,name="complete_chapter_progress"),
re_path(r'^user/download-attachment/(?P<pk>.*)/$',views.download_attachment,name="download-attachment"),
re_path(r'^user/download-all-attachment/(?P<pk>.*)/$',views.download_all_documents,name="download-all-attachment"),
   
    

]