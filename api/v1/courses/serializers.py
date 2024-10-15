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
    
class ViewChapterDetail(serializers.ModelSerializer):
    course_name=serializers.CharField(source='course_sub_content.course.title')
    documents = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()
    class Meta:
        model=Chapter
        fields=['id','video_url','thumbnail','title','duration','description','course_name','documents','links']
    
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