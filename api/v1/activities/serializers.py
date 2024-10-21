from rest_framework import serializers

from django.db.models import Sum, Count
from django.db.models import Avg

from accounts.models import *
from general.encryptions import encrypt,decrypt

from datetime import datetime
from . functions import *
from activities.models import *
from courses.models import *


class ListWebinarSerializer(serializers.ModelSerializer):
    category=serializers.CharField(source='category.name')
    join_date=serializers.SerializerMethodField()
    
    class Meta:
        model=Webinar
        fields=['id','category','title','host_name','start_time','end_time','join_link','image','join_date']
    
    def get_join_date(self,instance):
        formatted_date = instance.event_date.strftime("%d %b %Y")
        formatted_time = instance.event_date.strftime("%H:%M:%S")  # Keep time format as before
        return f"{formatted_date}"

class ListUserAssessmentAttemptHistorySerializer(serializers.ModelSerializer):
    date_added = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()

    class Meta:
        model = UserAssessmentAttempt
        fields = ['id', 'attempt_number', 'total_score', 'date_added', 'feedback']

    def get_date_added(self, obj):
        return obj.date_added.strftime("%b %d %I %p")

    def get_feedback(self, obj):
        # Assuming there's a Feedback model linked to UserAssessmentAttempt with a ForeignKey field named `user_assessment_attempt`
        feedback = AssessmentAttemptFeedback.objects.filter(user_attempt=obj, user=obj.user).first()
        if feedback:
            return {
                "id": feedback.id,
                "comment": feedback.comment,
                "date_added": feedback.date_added.strftime("%b %d %I %p"),
            }
        return None


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id','mark', 'question_text', 'answers']

class UserAnswerDetailSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    selected_answer_id = serializers.SerializerMethodField()
    correct_answer_id = serializers.SerializerMethodField()

    class Meta:
        model = UserAnswer
        fields = ['question', 'selected_answer_id', 'correct_answer_id', 'marks_awarded']

    def get_selected_answer_id(self, obj):
        return obj.answer.id

    def get_correct_answer_id(self, obj):
        # Find the correct answer for this question
        correct_answer = obj.question.answers.filter(is_correct=True).first()
        return correct_answer.id if correct_answer else None

class UserAssessmentAttemptDetailSerializer(serializers.ModelSerializer):
    date_added = serializers.SerializerMethodField()
    user_answers = UserAnswerDetailSerializer(many=True, source='user_answers_attempt', read_only=True)

    class Meta:
        model = UserAssessmentAttempt
        fields = ['id', 'attempt_number', 'date_added', 'total_score', 'user_answers']

    def get_date_added(self, obj):
        return obj.date_added.strftime("%b %d %I %p")

class AssessmentAttemptFeedbackSerializer(serializers.Serializer):
    comment=serializers.CharField()


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'name', 'file']

class TaskDetailSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, source='task_attachments')
    course_title = serializers.CharField(source='course_sub_content.course.title')

    class Meta:
        model = Task
        fields = ['id','course_title', 'title', 'description', 'task', 'attachments', 'instructions']