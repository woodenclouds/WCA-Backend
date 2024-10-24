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
class ListAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['id', 'title']

class ListTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title']

class ListCourseSubcontentSidebar(serializers.ModelSerializer):
    total_contents = serializers.SerializerMethodField()

    class Meta:
        model = CourseSubContent
        fields = ['id', 'title', 'position', 'type', 'total_contents']

    def get_total_contents(self, obj):
        # Check the type of CourseSubContent
        if obj.type == 'assessment':
            # If type is assessment, return the total number of assessments
            return obj.assessments.count()
        elif obj.type=='task':
            return obj.tasks.count()
        else:
            # If type is chapter, count the published chapters
            return obj.chapters.filter(is_published=True).count()

class ListChapterofSubcontentSidebar(serializers.ModelSerializer):
    is_completed=serializers.SerializerMethodField()
    latest_user_progress_id=serializers.SerializerMethodField()
    class Meta:
        model=Chapter
        fields=['id','title','thumbnail','duration','is_completed','position','latest_user_progress_id']
    def get_is_completed(self, obj):
        user = self.context.get('request').user
        return UserProgress.objects.filter(user=user, chapter=obj, is_completed=True).exists()
    def get_latest_user_progress_id(self, obj):
        user = self.context.get('request').user
        # Get the first user progress object, if it exists
        user_progress = UserProgress.objects.filter(user=user, chapter=obj).first()
        # Check if user_progress is not None before accessing its id
        return user_progress.id if user_progress else None
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
        request=self.context['request']
        documents = obj.attachments.filter(file__isnull=False, url='')
        return [
            {
                'id': document.id,
                'name': document.name,
                'file': request.build_absolute_uri(document.file.url) if document.file else None
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
        print(f"Total chapters: {total_chapters}")

        # Get the number of chapters the user has completed
        completed_chapters = UserProgress.objects.filter(
            user=user, chapter__course_sub_content__course=obj, is_completed=True
        ).count()
        print(f"Completed chapters: {completed_chapters}")

        # Get total number of assessments for the course
        total_assessments = Assessment.objects.filter(course_sub_content__course=obj).count()
        print(f"Total assessments: {total_assessments}")

        # Get the number of assessments the user has passed
        passed_assessments = UserAssessmentAttempt.objects.filter(
            user=user, assessment__course_sub_content__course=obj, status='passed'
        ).distinct().count()
        print(f"Passed assessments: {passed_assessments}")

        # Get total number of tasks for the course
        total_tasks = Task.objects.filter(course_sub_content__course=obj).count()
        print(f"Total tasks: {total_tasks}")

        # Get the number of tasks the user has submitted
        submitted_tasks = TaskSubmission.objects.filter(
            user=user, task__course_sub_content__course=obj
        ).count()
        print(f"Submitted tasks: {submitted_tasks}")

        # Calculate progress for each component
        chapter_progress = (completed_chapters / total_chapters) * 100 if total_chapters > 0 else 0
        assessment_progress = (passed_assessments / total_assessments) * 100 if total_assessments > 0 else 0
        task_progress = (submitted_tasks / total_tasks) * 100 if total_tasks > 0 else 0

        # Average the progress values and clamp between 0 and 100
        user_progress = (chapter_progress + assessment_progress + task_progress) / 3
        user_progress = max(0, min(100, user_progress))  # Ensure progress is between 0 and 100

        return round(user_progress, 2)  # Rounded to 2 decimal places

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text']

class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'mark', 'answers']

    def get_answers(self, obj):
        # Shuffle the answers for each question
        answers = list(obj.answers.all())
        random.shuffle(answers)
        return AnswerSerializer(answers, many=True).data

class AssessmentDetailSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course_sub_content.course.title')
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = [
            'id', 'title', 'type', 'max_attempts', 'total_questions', 
            'scoring_policy', 'passing_score', 'course_title', 'questions'
        ]

    def get_questions(self, obj):
        # Shuffle the questions for each assessment
        questions = list(obj.questions.all())
        random.shuffle(questions)
        
        # Select up to 10 questions randomly
        selected_questions = questions[:obj.total_questions]
        
        return QuestionSerializer(selected_questions, many=True).data