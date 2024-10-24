from django.urls import re_path, path
from .  import  views

app_name = 'api_v1_activities'

urlpatterns = [


re_path(r'^user/get-webinar-list/$', views.get_webinar_list, name="get_webinar_list"),
re_path(r'^user/get-latest-assessment-summary/(?P<pk>.*)/$', views.latest_attempt_summary, name="get_latest_assessment_summary"),
re_path(r'^user/get-assessment-attempt-history/(?P<pk>.*)/$',views.get_assessment_attempt_history_list,name="list of users assessment attempt history of that assessment"),
re_path(r'^user/assessment-attempt-detail/(?P<pk>.*)/$',views.get_user_attempt_detail,name="assessment attempt detail"),
re_path(r'^user/submit-assessment/(?P<pk>.*)/$',views.submit_assessment,name="submit_assessment"),
re_path(r'^user/purchase-course/$', views.purchase_course, name="purchase_course"),
re_path(r'^user/update-progress/(?P<pk>.*)/$',views.update_user_progress,name="update_user_progress"),
re_path(r'^user/complete-chapter-progress/(?P<pk>.*)/$',views.user_complete_chapter_progress,name="complete_chapter_progress"),
re_path(r'^user/download-attachment/(?P<pk>.*)/$',views.download_attachment,name="download-attachment"),
re_path(r'^user/download-all-attachment/(?P<pk>.*)/$',views.download_all_documents,name="download-all-attachment"),

re_path(r'^user/add-assessment-feedback/$', views.add_assessment_feedback, name="Add Feedback for user assessment attempt"),
re_path(r'^user/task-detail/(?P<pk>.*)/$',views.get_task_detail,name="get task detail"),
re_path(r'^user/submit-task/$', views.submit_task, name="submit-task"),

re_path(r'^upload-file/$', views.upload_file, name="upload-file"),
re_path(r'^delete-file/$', views.delete_attachments, name="cancel-file"),

re_path(r'^render-certificate/$', views.render_html, name="cancel-file"),
re_path(r'^user/generate-certificate/$', views.generate_certificate, name="generate-certificate"),

   
    

]