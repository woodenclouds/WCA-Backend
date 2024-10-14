from django.contrib import admin
from . models import *

# Register your models here.
class CoursePurchaseAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "course", "is_certificate_eligible")
    list_filter = ("user", "course", "is_certificate_eligible", "date_added", "date_updated")
    search_fields = ("user__first_name", "user__last_name", "course__name")

admin.site.register(CoursePurchase, CoursePurchaseAdmin)


class WebinarAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "event_date", "start_time", "end_time")
    list_filter = ("category", "event_date", "date_added", "date_updated")
    search_fields = ("title", "category__name")

admin.site.register(Webinar, WebinarAdmin)


class UserProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "chapter", "is_completed")
    list_filter = ("user", "chapter", "is_completed", "date_added", "date_updated")
    search_fields = ("user__first_name", "user__last_name", "chapter__title")

admin.site.register(UserProgress, UserProgressAdmin)


class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "type", "max_attempts", "passing_score", "total_questions", "scoring_policy", "course_sub_content")
    list_filter = ("type", "scoring_policy", "date_added", "date_updated")
    search_fields = ("title", "course_sub_content__name")

admin.site.register(Assessment, AssessmentAdmin)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "assessment", "question_text", "mark")
    list_filter = ("assessment", "date_added", "date_updated")
    search_fields = ("question_text", "assessment__title")

admin.site.register(Question, QuestionAdmin)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "text", "is_correct")
    list_filter = ("is_correct", "question", "date_added", "date_updated")
    search_fields = ("text", "question__question_text")

admin.site.register(Answer, AnswerAdmin)


class UserAssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "assessment", "attempt_number", "total_score", "status")
    list_filter = ("status", "user", "assessment", "date_added", "date_updated")
    search_fields = ("user__first_name", "user__last_name", "assessment__title")

admin.site.register(UserAssessmentAttempt, UserAssessmentAttemptAdmin)


class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "user_attempt", "question", "answer", "marks_awarded")
    list_filter = ("user_attempt", "question", "answer", "date_added", "date_updated")
    search_fields = ("question__question_text", "user_attempt__assessment__title")

admin.site.register(UserAnswer, UserAnswerAdmin)


class AssessmentAttemptFeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "user_attempt", "comment", "user")
    list_filter = ("user_attempt", "user", "date_added", "date_updated")
    search_fields = ("user__first_name", "user__last_name", "comment")

admin.site.register(AssessmentAttemptFeedback, AssessmentAttemptFeedbackAdmin)


class CertificateAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "issued_on", "user", "course")
    list_filter = ("user", "course", "issued_on", "date_added", "date_updated")
    search_fields = ("full_name", "user__first_name", "user__last_name", "course__name")

admin.site.register(Certificate, CertificateAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course_sub_content")
    list_filter = ("course_sub_content", "date_added", "date_updated")
    search_fields = ("title", "course_sub_content__name")

admin.site.register(Task, TaskAdmin)


class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "task", "status", "point")
    list_filter = ("status", "task", "user", "date_added", "date_updated")
    search_fields = ("user__first_name", "user__last_name", "task__title")

admin.site.register(TaskSubmission, TaskSubmissionAdmin)
