from django.urls import re_path, path
from .  import  views

app_name = 'api_v1_courses'

urlpatterns = [

re_path(r'^user/get-course-list/$', views.get_courses_list, name="get_courses_list"),
re_path(r'^user/get-enrolled-course-list/$', views.get_purchased_courses_list, name="get_enrolled_course"),
re_path(r'^user/course-sub-content-sidebar/(?P<pk>.*)/$',views.get_course_sub_content_sidebar,name="get_course_sub_content_dashboard"),
re_path(r'^user/get-contents-of-course-sub-content-sidebar/(?P<pk>.*)/$',views.get_chapters_of_sub_content_sidebar,name="get_chapters_of_subcontent_sidebar"),
re_path(r'^user/get-chapter-detail/(?P<pk>.*)/$',views.get_chapter_detail,name="get_chapter_detail"),
re_path(r'^user/get-assessment-detail/(?P<pk>.*)/$',views.get_assessment_details,name="get_assesment_detail"),
re_path(r'^user/get-course-detail/(?P<pk>.*)/$',views.get_course_detail,name="get_course_detail"),

    

]