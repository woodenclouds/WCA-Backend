from django.contrib import admin

from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username","phone","is_verified"]
    
class SocialMediaLinksAdmin(admin.ModelAdmin):
    list_display = ("id","name","user")
    list_filter = ("user","name", "date_added", "date_updated")
    search_fields = ("user__first_name", "user__last_name")

admin.site.register(SocialMediaLink, SocialMediaLinksAdmin)

class OTPAdmin(admin.ModelAdmin):
    list_display = ("id","phone","otp","is_verified",)
    list_filter = ("phone","is_verified","date_added", "date_updated")
    search_fields = ("otp",)

admin.site.register(OTP, OTPAdmin)

class UserInline(admin.TabularInline):
    model = Group.user_set.through  # Access the through table that connects User and Group
    extra = 0  # No extra empty user slots

# Customize the Group admin
class GroupAdmin(admin.ModelAdmin):
    inlines = [UserInline]  # Show the UserInline in Group admin

# Unregister the default Group admin and register the customized one
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)