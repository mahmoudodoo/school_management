from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.core.validators import FileExtensionValidator


# Custom User model to support both Student and Parent
class User(AbstractUser):
   USER_TYPE_CHOICES = (
       ('parent', 'Parent'),
       ('student', 'Student'),
   )
   user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='parent')
   phone_number = models.CharField(max_length=15, blank=True, null=True)
   email = models.EmailField(unique=True)


   # Add unique related_name for groups and user_permissions
   groups = models.ManyToManyField(
       'auth.Group',
       verbose_name='groups',
       blank=True,
       help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
       related_name="core_user_groups",  # Unique related_name
       related_query_name="core_user",
   )
   user_permissions = models.ManyToManyField(
       'auth.Permission',
       verbose_name='user permissions',
       blank=True,
       help_text='Specific permissions for this user.',
       related_name="core_user_permissions",  # Unique related_name
       related_query_name="core_user",
   )


   def __str__(self):
       return self.username


# Parent model (extends User)
class Parent(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
   # Additional fields for Parent (if needed)
   address = models.CharField(max_length=255, blank=True, null=True)


   def __str__(self):
       return self.user.get_full_name()


# Student model (extends User)
class Student(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
   parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='students', blank=True, null=True)
   first_name = models.CharField(max_length=100)
   last_name = models.CharField(max_length=100)
   date_of_birth = models.DateField()
   absence_limit = models.IntegerField(default=10)


   def __str__(self):
       return f"{self.first_name} {self.last_name}"


   def is_absentee(self):
       absences = self.attendances.filter(status='Absent').count()
       return absences > self.absence_limit


# Attendance model
class Attendance(models.Model):
   student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
   date = models.DateField()
   status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])


   def __str__(self):
       return f"{self.student} - {self.date} - {self.status}"


# Subject model
class Subject(models.Model):
   name = models.CharField(max_length=100)


   def __str__(self):
       return self.name


# Academic Performance model
class AcademicPerformance(models.Model):
   student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_performances')
   subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
   grade = models.CharField(max_length=2)


   def __str__(self):
       return f"{self.student} - {self.subject} - {self.grade}"


   def is_failing(self):
       return self.grade in ['F', 'D']


   def is_excelling(self):
       return self.grade in ['A', 'A+']


# Notification model
class Notification(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
   message = models.TextField()
   timestamp = models.DateTimeField(auto_now_add=True)
   is_read = models.BooleanField(default=False)


   def __str__(self):
       return f"{self.user} - {self.message}"


# Report model
class Report(models.Model):
   student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='reports')
   report_type = models.CharField(max_length=50, choices=[('Attendance', 'Attendance'), ('Performance', 'Performance')])
   generated_at = models.DateTimeField(auto_now_add=True)
   content = models.TextField()


   def __str__(self):
       return f"{self.student} - {self.report_type} Report"
  
  




# Add these models at the end of your existing models


class AbsenceExcuse(models.Model):
   STATUS_CHOICES = [
       ('pending', 'Pending'),
       ('approved', 'Approved'),
       ('rejected', 'Rejected'),
   ]
  
   student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='absence_excuses')
   attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='excuses', null=True, blank=True)
   date = models.DateField(default=timezone.now)
   reason = models.TextField()
   supporting_document = models.FileField(
       upload_to='absence_excuses/',
       validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
       blank=True,
       null=True
   )
   status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
   submitted_at = models.DateTimeField(auto_now_add=True)
   reviewed_by = models.ForeignKey(
       User,
       on_delete=models.SET_NULL,
       null=True,
       blank=True,
       related_name='reviewed_excuses'
   )
   reviewed_at = models.DateTimeField(null=True, blank=True)
   response_notes = models.TextField(blank=True)


   def __str__(self):
       return f"Excuse for {self.student} on {self.date} - {self.get_status_display()}"


   class Meta:
       ordering = ['-submitted_at']
       verbose_name = "Absence Excuse"
       verbose_name_plural = "Absence Excuses"


class Assignment(models.Model):
   subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
   title = models.CharField(max_length=200)
   description = models.TextField()
   due_date = models.DateTimeField()
   created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
   created_at = models.DateTimeField(auto_now_add=True)
   max_points = models.PositiveIntegerField(default=100)
   is_published = models.BooleanField(default=True)


   def __str__(self):
       return f"{self.title} - {self.subject}"


   class Meta:
       ordering = ['-due_date']


class AssignmentSubmission(models.Model):
   assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
   student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submitted_assignments')
   submission_file = models.FileField(
       upload_to='assignment_submissions/',
       validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'txt', 'zip', 'rar'])],
   )
   submitted_at = models.DateTimeField(auto_now_add=True)
   notes = models.TextField(blank=True)
   grade = models.PositiveIntegerField(null=True, blank=True)
   feedback = models.TextField(blank=True)
   is_late = models.BooleanField(default=False)


   def __str__(self):
       return f"{self.student}'s submission for {self.assignment}"


   def save(self, *args, **kwargs):
       if self.assignment.due_date and self.submitted_at:
           self.is_late = self.submitted_at > self.assignment.due_date
       super().save(*args, **kwargs)


   class Meta:
       ordering = ['-submitted_at']
       unique_together = ['assignment', 'student']