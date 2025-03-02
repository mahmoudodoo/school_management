from django.contrib import admin
from .models import Parent, Student, Attendance, Subject, AcademicPerformance

admin.site.register(Parent)
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Subject)
admin.site.register(AcademicPerformance)