from rest_framework import serializers

from django.db.models import Sum, Count
from django.db.models import Avg

from accounts.models import *
from general.encryptions import encrypt,decrypt

from datetime import datetime
from courses.models import *
from activities.models import *
from . functions import *


class ListCourseSerializer(serializers.ModelSerializer):
    total_contents=serializers.SerializerMethodField()
    class Meta:
        model=Course
        fields=['id','title','instructor_name','image','total_contents']

    def get_total_contents(self,obj):
        return obj.sub_contents.filter(is_deleted=False).count()

class ListCourseSubcontentSidebar(serializers.ModelSerializer):
    total_contents=serializers.SerializerMethodField()

    class Meta:
        model=CourseSubContent
        fields=['id','title','position','type','total_contents']
    def get_total_contents(self,obj):
        return obj.chapters.filter(is_published=True).count()
    

class ListChapterofSubcontentSidebar(serializers.ModelSerializer):
    is_completed=serializers.SerializerMethodField()
    class Meta:
        model=Chapter
        fields=['id','title','thumbnail','duration','is_completed','position']
    def get_is_completed(self, obj):
        user = self.context.get('request').user
        return UserProgress.objects.filter(user=user, chapter=obj, is_completed=True).exists()
#title,duration,instructor_name,language,is_certificate_available,course_fee,description
class ViewCourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=Course
        fields=['id','title','duration','instructor_name','language','is_certificate_available','course_fee','description']
class ViewChapterDetail(serializers.ModelSerializer):
    course_name=serializers.CharField(source='course_sub_content.course.title')
    documents = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()
    course_detail = ViewCourseDetailSerializer(source='course_sub_content.course', read_only=True)
    
    class Meta:
        model=Chapter
        fields=['id','video_url','thumbnail','title','duration','description','course_name','documents','links','is_preview','course_detail']
    
    def get_documents(self, obj):
        # Filter attachments that have a file but no URL
        documents = obj.attachments.filter(file__isnull=False, url='')
        return [
            {
                'id': document.id,
                'name': document.name,
                'file': document.file.url if document.file else None
            }
            for document in documents
        ]

    def get_links(self, obj):
        # Filter attachments that have a non-empty URL but no file
        links = obj.attachments.filter(url__isnull=False, file='')
        return [
            {
                'id': link.id,
                'name': link.name,
                'link': link.url
            }
            for link in links
        ]


class EnrolledCourseSerializer(serializers.ModelSerializer):
    total_subcontents = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'image', 'total_subcontents', 'user_progress']

    def get_total_subcontents(self, obj):
        # Get total number of subcontents for the course
        return obj.sub_contents.count()

    def get_user_progress(self, obj):
        # Get the user from the context
        user = self.context['request'].user

        # Get total number of chapters for the course
        total_chapters = Chapter.objects.filter(course_sub_content__course=obj).count()
        print(f"total chapters {total_chapters}")

        # Get the number of chapters the user has completed
        completed_chapters = UserProgress.objects.filter(
            user=user, chapter__course_sub_content__course=obj, is_completed=True
        ).count()
        print("completed chapters",completed_chapters)

        # Calculate the user progress value as a percentage
        user_progress = (completed_chapters / total_chapters) * 100 if total_chapters > 0 else 0
        return round(user_progress, 2)  # Rounded to 2 decimal places