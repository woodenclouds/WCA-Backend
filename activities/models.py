from django.db import models
from accounts.models import User
from general.models import BaseModel
from datetime import datetime
from . functions import get_auto_id
# Create your models here.


# Constants for Choice Fields
ASSESSMENT_TYPE_CHOICES = (
    ('graded', 'Graded'),
    ('practice', 'Practice'),
)

SCORING_POLICY_CHOICES = (
    ('highest_score', 'Highest Score'),
)

STATUS_CHOICES = (
    ('failed', 'Failed'),
    ('passed', 'Passed'),
)

ATTACHMENT_TYPE_CHOICES = (
    ('link', 'Link'),
    ('file', 'File'),
)


class CoursePurchase(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_purchases')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='purchases')
    is_certificate_eligible = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(CoursePurchase)
            self.auto_id = auto_id
        super(CoursePurchase, self).save(*args, **kwargs)

    class Meta:
        db_table = 'activities_course_purchase'
        verbose_name = 'Course Purchase'
        verbose_name_plural = 'Course Purchases'
        ordering = ('date_added',)


# Webinar Model
class Webinar(BaseModel):
    category = models.ForeignKey('courses.Category', on_delete=models.CASCADE, related_name='webinars')
    title = models.CharField(max_length=255)
    join_link = models.CharField(max_length=500)
    event_date = models.DateField()
    start_time = models.CharField()
    end_time = models.CharField()
    host_name=models.CharField(null=True,blank=True)
    image=models.ImageField(upload_to="webinar",null=True,blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(Webinar)
            self.auto_id = auto_id
        super(Webinar, self).save(*args, **kwargs)

    class Meta:
        db_table = 'activities_webinar'
        verbose_name = 'Webinar'
        verbose_name_plural = 'Webinars'
        ordering = ('event_date',)


# User Progress Model
class UserProgress(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    chapter = models.ForeignKey('courses.Chapter', on_delete=models.CASCADE, related_name='user_progress')
    is_completed = models.BooleanField(default=False)
    completed_time=models.DateTimeField(null=True,blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(UserProgress)
            self.auto_id = auto_id
        super(UserProgress, self).save(*args, **kwargs)

    class Meta:
        db_table = 'activities_user_progress'
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'
        ordering = ('date_added',)


# Assessment Model
class Assessment(BaseModel):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES)
    max_attempts = models.PositiveIntegerField(default=1)
    passing_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_questions = models.PositiveIntegerField()
    scoring_policy = models.CharField(max_length=20, choices=SCORING_POLICY_CHOICES)
    course_sub_content = models.ForeignKey('courses.CourseSubContent', on_delete=models.CASCADE, related_name='assessments')

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(Assessment)
            self.auto_id = auto_id
        super(Assessment, self).save(*args, **kwargs)
    def __str__(self):
        return f"{self.course_sub_content.course.title} assessment"

    class Meta:
        db_table = 'activities_assessment'
        verbose_name = 'Assessment'
        verbose_name_plural = 'Assessments'
        ordering = ('date_added',)


# Question Model
class Question(BaseModel):
    assessment = models.ForeignKey('Assessment', on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(null=True,blank=True)
    mark = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(Question)
            self.auto_id = auto_id
        super(Question, self).save(*args, **kwargs)

    class Meta:
        db_table = 'activities_question'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ('date_added',)
    def __str__(self):
        return f"{self.question_text}"


# Answer Model
class Answer(BaseModel):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(null=True,blank=True)
    is_correct = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(Answer)
            self.auto_id = auto_id
        super(Answer, self).save(*args, **kwargs)
    def __str__(self):
        return f"{self.text}"

    class Meta:
        db_table = 'activities_answer'
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        ordering = ('date_added',)


# User Assessment Attempt Model
class UserAssessmentAttempt(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_attempts')
    assessment = models.ForeignKey('Assessment', on_delete=models.CASCADE, related_name='user_attempts')
    attempt_number = models.PositiveIntegerField()
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    max_score=models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(UserAssessmentAttempt)
            self.auto_id = auto_id
        super(UserAssessmentAttempt, self).save(*args, **kwargs)
    def __str__(self):
        return f"{self.user}s {self.assessment} attempt no {self.attempt_number}"

    class Meta:
        db_table = 'activities_user_assessment_attempt'
        verbose_name = 'User Assessment Attempt'
        verbose_name_plural = 'User Assessment Attempts'
        ordering = ('attempt_number',)


# User Answer Model
class UserAnswer(BaseModel):
    user_attempt = models.ForeignKey('UserAssessmentAttempt', on_delete=models.CASCADE, related_name='user_answers_attempt')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='user_answers_question')
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, related_name='user_answers_answer')
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(UserAnswer)
            self.auto_id = auto_id
        super(UserAnswer, self).save(*args, **kwargs)

    class Meta:
        db_table = 'activities_user_answer'
        verbose_name = 'User Answer'
        verbose_name_plural = 'User Answers'
        ordering = ('date_added',)


# Assessment Attempt Feedback Model
class AssessmentAttemptFeedback(BaseModel):
    user_attempt = models.ForeignKey('UserAssessmentAttempt', on_delete=models.CASCADE, related_name='feedback')
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_feedback')

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(AssessmentAttemptFeedback)
            self.auto_id = auto_id
        super(AssessmentAttemptFeedback, self).save(*args, **kwargs)

    class Meta:
        db_table = 'activities_assessment_attempt_feedback'
        verbose_name = 'Assessment Attempt Feedback'
        verbose_name_plural = 'Assessment Attempt Feedback'
        ordering = ('date_added',)


# Certificate Model
class Certificate(BaseModel):
    full_name = models.CharField(max_length=255)
    issued_on = models.DateField(default=datetime.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='certificates')

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(Certificate)
            self.auto_id = auto_id
        super(Certificate, self).save(*args, **kwargs)

    class Meta:
        db_table = 'activities_certificate'
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        ordering = ('issued_on',)


# Task Model
class Task(BaseModel):
    course_sub_content = models.ForeignKey('courses.CourseSubContent', on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    task = models.TextField(null=True,blank=True)
    instructions = models.TextField()

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(Task)
            self.auto_id = auto_id
        super(Task, self).save(*args, **kwargs)

    class Meta:
        db_table = 'activities_task'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ('date_added',)


# Task Submission Model
class TaskSubmission(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_submissions')
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='submissions')
    submission_text = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    point = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self._state.adding:
            auto_id = get_auto_id(TaskSubmission)
            self.auto_id = auto_id
        super(TaskSubmission, self).save(*args, **kwargs)

    class Meta:
        db_table = 'activities_task_submission'
        verbose_name = 'Task Submission'
        verbose_name_plural = 'Task Submissions'
        ordering = ('date_added',)
