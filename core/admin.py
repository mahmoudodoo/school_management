from django.contrib import admin
from .models import User, Parent, Student, Attendance, Subject, AcademicPerformance, Notification, Report
from custom_admin import custom_admin_site  # Import the custom admin site

# Register your models here.

@admin.register(User, site=custom_admin_site)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'phone_number')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('user_type',)

@admin.register(Parent, site=custom_admin_site)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'address')
    search_fields = ('user__username', 'user__email', 'address')

@admin.register(Student, site=custom_admin_site)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'parent', 'first_name', 'last_name', 'date_of_birth')
    search_fields = ('user__username', 'first_name', 'last_name')
    list_filter = ('parent',)

@admin.register(Attendance, site=custom_admin_site)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
    search_fields = ('student__first_name', 'student__last_name', 'date')
    list_filter = ('status', 'date')

@admin.register(Subject, site=custom_admin_site)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(AcademicPerformance, site=custom_admin_site)
class AcademicPerformanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'grade')
    search_fields = ('student__first_name', 'student__last_name', 'subject__name')
    list_filter = ('grade', 'subject')

@admin.register(Notification, site=custom_admin_site)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'timestamp', 'is_read')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read', 'timestamp')

@admin.register(Report, site=custom_admin_site)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'report_type', 'generated_at')
    search_fields = ('student__first_name', 'student__last_name', 'report_type')
    list_filter = ('report_type', 'generated_at')
