from django.db import models
from accounts.models import *
from general.models import BaseModel
from datetime import datetime, timedelta




CONTENT_TYPE_CHOICES = (
    ('chapter', 'Chapter'),
    ('assessment', 'Assessment'),
    ('task', 'Task'),
)
ATTACHMENT_TYPE_CHOICES = (
        ('doc', 'Document'),
        ('link', 'Link'),
    )



class Category(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"
    
    def save(self, *args, **kwargs):
        if self._state.adding:
                auto_id = get_auto_id(Category)
                self.auto_id = auto_id

        super(Category, self).save(*args, **kwargs)
    
    class Meta:
        db_table = "courses_category"
        verbose_name = "Category"
        verbose_name_plural = "Category"
        ordering = ("date_added",)
    

class Course(BaseModel):
    title = models.CharField(max_length=255)
    duration = models.CharField(max_length=100)  
    instructor_name = models.CharField(max_length=255)
    language = models.CharField(max_length=100)
    is_certificate_available = models.BooleanField(default=False)
    course_fee = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE,related_name='courses')  
    is_published = models.BooleanField(default=False)
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.title}"
    
    def save(self, *args, **kwargs):
        if self._state.adding:
                auto_id = get_auto_id(Course)
                self.auto_id = auto_id

        super(Course, self).save(*args, **kwargs)

    class Meta:
        db_table = "courses_course"
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ("date_added",)


class CourseSubContent(BaseModel):
    title = models.CharField(max_length=255)
    position = models.PositiveIntegerField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='sub_contents')
    type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='chapter')

    def __str__(self):
        return f"{self.title}"
    
    def save(self, *args, **kwargs):
        if self._state.adding:
                auto_id = get_auto_id(CourseSubContent)
                self.auto_id = auto_id

        super(CourseSubContent, self).save(*args, **kwargs)

    class Meta:
        db_table = "courses_course_sub_content"
        verbose_name = "Course Sub Content"
        verbose_name_plural = "Course Sub Contents"
        ordering = ("position",)

class Chapter(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_url = models.CharField(max_length=500)
    position = models.PositiveIntegerField()
    is_published = models.BooleanField(default=False)
    course_sub_content = models.ForeignKey('CourseSubContent', on_delete=models.CASCADE,related_name='chapters')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self._state.adding:
                auto_id = get_auto_id(Chapter)
                self.auto_id = auto_id

        super(Chapter, self).save(*args, **kwargs)

    class Meta:
        db_table = "courses_chapter"
        verbose_name = "Chapter"
        verbose_name_plural = "Chapters"
        ordering = ("position",)
class Attachment(BaseModel):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=500)
    chapter = models.ForeignKey('Chapter', on_delete=models.CASCADE,related_name='attachments')
    type = models.CharField(max_length=10, choices=ATTACHMENT_TYPE_CHOICES)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self._state.adding:
                auto_id = get_auto_id(Attachment)
                self.auto_id = auto_id

        super(Attachment,self).save(*args, **kwargs)

    class Meta:
        db_table = "courses_attachments"
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"
        ordering = ("name",)
