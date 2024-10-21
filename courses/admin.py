from django.contrib import admin
from . models import *
from django.urls import reverse
from django.utils.html import format_html
from .models import Course, CourseSubContent, Chapter
from activities.models import Assessment,Task
# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    list_filter = ("date_added", "date_updated")

admin.site.register(Category, CategoryAdmin)

# class CourseAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", "instructor_name", "is_published", "course_fee")
#     search_fields = ("title", "instructor_name", "description")
#     list_filter = ("is_published", "category", "date_added", "date_updated")

# admin.site.register(Course, CourseAdmin)

# class CourseSubContentAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", "course", "type", "position")
#     search_fields = ("title", "course__title")
#     list_filter = ("course", "type", "date_added", "date_updated")

# admin.site.register(CourseSubContent, CourseSubContentAdmin)

# class ChapterAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", "course_sub_content", "is_published", "position")
#     search_fields = ("title", "course_sub_content__title")
#     list_filter = ("course_sub_content", "is_published", "date_added", "date_updated")

# admin.site.register(Chapter, ChapterAdmin)

# class AttachmentAdmin(admin.ModelAdmin):
#     list_display = ("id", "name", "chapter", "type")
#     search_fields = ("name", "chapter__title")
#     list_filter = ("chapter", "type", "date_added", "date_updated")

# admin.site.register(Attachment, AttachmentAdmin)

# Inline for managing attachments within the chapter detail page
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1  # Allows adding one new attachment
    fields = ['name', 'url', 'type','file']  # Display fields for attachments + edit link
    
class TaskAttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1  # Allows adding one new attachment
    fields = ['name','type','file']  # Display fields for attachments + edit link
    

# Admin for the Chapter, with inline attachments
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'is_published']  # Display key fields + edit link
    search_fields = ['title']

    # Adding the inline attachments
    inlines = [AttachmentInline]

   

    # Extra context for the change view (for customizing if needed)
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = True  # Keep save and continue editing option
        return super(ChapterAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context
        )


class CourseSubContentInline(admin.TabularInline):
    model = CourseSubContent
    extra = 0  # No empty extra forms
    fields = ['title', 'position', 'type', 'edit_link']  # Displaying the link to edit
    readonly_fields = ['edit_link']  # This field should be read-only

    def edit_link(self, obj):
        if obj.pk:  # Check if the object already exists
            url = reverse('admin:courses_coursesubcontent_change', args=[obj.pk])
            return format_html(f'<a href="{url}">View</a>')
        return "Save and Continue Editing"

    edit_link.short_description = "View SubCourseContent"  # Label for the column

    


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor_name', 'is_published', 'course_fee')
    list_filter = ('is_published', 'category')
    search_fields = ('title', 'instructor_name', 'language')

    inlines = [CourseSubContentInline]  # Adding the inline to the Course detail page


# Inline for Chapter with edit link
class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0  # No extra empty forms
    fields = ['title', 'description', 'video_url', 'position', 'is_published', 'edit_link']  # Display all fields for chapters + edit link
    readonly_fields = ['edit_link']  # Make edit link read-only

    def edit_link(self, obj):
        if obj.pk:  # Check if the object already exists (has been saved)
            url = reverse('admin:courses_chapter_change', args=[obj.pk])  # Correct reverse name
            return format_html(f'<a href="{url}">View</a>')
        return "Save to enable editing"  # Placeholder if the object hasn't been saved yet

    edit_link.short_description = "View Chapter"  # Label for the edit link column

    # Ensuring that the inline forms save correctly
    def has_add_permission(self, request, obj):
        # Allow adding chapters if the CourseSubContent exists
        return obj is not None

    def has_change_permission(self, request, obj=None):
        # Allow changing chapters
        return True

class AssessmentInline(admin.TabularInline):
    model = Assessment
    extra = 0  # No extra empty forms
    fields = ['title', 'type', 'max_attempts', 'passing_score', 'total_questions', 'scoring_policy', 'edit_link']
    readonly_fields = ['edit_link']

    def edit_link(self, obj):
        if obj.pk:
            url = reverse('admin:activities_assessment_change', args=[obj.pk])
            return format_html(f'<a href="{url}">View</a>')
        return "Save to enable editing"

    edit_link.short_description = "View Assessment"

    def has_add_permission(self, request, obj):
        return obj is not None

    def has_change_permission(self, request, obj=None):
        return True
class TaskInline(admin.TabularInline):
    model = Task
    extra = 0  # No extra empty forms
    fields = ['title', 'description', 'instructions','task', 'edit_link']
    readonly_fields = ['edit_link']

    def edit_link(self, obj):
        if obj.pk:
            url = reverse('admin:activities_task_change', args=[obj.pk])
            return format_html(f'<a href="{url}">View</a>')
        return "Save to enable editing"

    edit_link.short_description = "View Assessment"

    def has_add_permission(self, request, obj):
        return obj is not None

    def has_change_permission(self, request, obj=None):
        return True

# Register CourseSubContent with the ability to manage chapters
@admin.register(CourseSubContent)
class CourseSubContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'position', 'type']
    search_fields = ['title', 'course__title']
    inlines = [ChapterInline, AssessmentInline,TaskInline]  # Add both ChapterInline and AssessmentInline

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = True
        return super(CourseSubContentAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context
        )