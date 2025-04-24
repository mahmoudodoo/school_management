from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from django.db.models import  Q 

# Custom User model to support both Student and Parent
class User(AbstractUser):
   USER_TYPE_CHOICES = (
       ('parent', 'Parent'),
       ('student', 'Student'),
       ('admin', 'Admin'),  # Added admin type for notification purposes
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
       related_name="core_user_groups",
       related_query_name="core_user",
   )
   user_permissions = models.ManyToManyField(
       'auth.Permission',
       verbose_name='user permissions',
       blank=True,
       help_text='Specific permissions for this user.',
       related_name="core_user_permissions",
       related_query_name="core_user",
   )


   def __str__(self):
       return self.username


   def is_admin(self):
       return self.user_type == 'admin' or self.is_superuser


# Parent model (extends User)
class Parent(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
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
   notification_type = models.CharField(max_length=50, blank=True, null=True)
   related_object_id = models.PositiveIntegerField(blank=True, null=True)
   related_content_type = models.CharField(max_length=50, blank=True, null=True)


   def __str__(self):
       return f"{self.user} - {self.message}"


   @classmethod
   def create_notification(cls, user, message, notification_type=None, related_object=None):
       notification = cls.objects.create(
           user=user,
           message=message,
           notification_type=notification_type
       )
      
       if related_object:
           notification.related_object_id = related_object.id
           notification.related_content_type = related_object.__class__.__name__
           notification.save()
      
       return notification


# Report model
class Report(models.Model):
   student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='reports')
   report_type = models.CharField(max_length=50, choices=[('Attendance', 'Attendance'), ('Performance', 'Performance')])
   generated_at = models.DateTimeField(auto_now_add=True)
   content = models.TextField()


   def __str__(self):
       return f"{self.student} - {self.report_type} Report"


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
    STATUS_CHOICES = [
       ('pending', 'Pending'),
       ('approved', 'Approved'),
       ('rejected', 'Rejected'),]
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
    satus = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')


    def __str__(self):
        return f"{self.student}'s submission for {self.assignment}"



    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student']


# Signal handlers for notifications


@receiver(post_save, sender=Report)
def notify_parent_on_new_report(sender, instance, created, **kwargs):
   if created:
       try:
           if instance.student.parent:
               message = f"New {instance.report_type} report available for {instance.student}"
               Notification.create_notification(
                   user=instance.student.parent.user,
                   message=message,
                   notification_type='new_report',
                   related_object=instance
               )
               print(f"Notification created for parent: {instance.student.parent.user}")  # Debugging
       except Exception as e:
           print(f"Error creating report notification: {e}")


@receiver(post_save, sender=Assignment)
def notify_students_on_new_assignment(sender, instance, created, **kwargs):
   if created and instance.is_published:
       try:
           students = Student.objects.all()
           message = f"New assignment in {instance.subject}: {instance.title} (Due: {instance.due_date.strftime('%Y-%m-%d')})"
          
           for student in students:
               Notification.create_notification(
                   user=student.user,
                   message=message,
                   notification_type='new_assignment',
                   related_object=instance
               )
           print(f"Notifications created for {students.count()} students")  # Debugging
       except Exception as e:
           print(f"Error creating assignment notifications: {e}")


@receiver(post_save, sender=AbsenceExcuse)
def handle_absence_excuse_notifications(sender, instance, created, **kwargs):
   try:
       if created:
           # Notify admin users when new excuse is submitted
           admin_users = get_user_model().objects.filter(Q(user_type='admin') | Q(is_superuser=True))
           message = f"New absence excuse submitted by {instance.student} for {instance.date}"
          
           for admin in admin_users.distinct():
               Notification.create_notification(
                   user=admin,
                   message=message,
                   notification_type='new_absence_excuse',
                   related_object=instance
               )
           print(f"Notifications created for {admin_users.count()} admins")  # Debugging
      
       # Always check for status change, not just in update_fields
       if not created and instance.status != instance._original_status:
           status_display = instance.get_status_display()
           message = f"Your absence excuse for {instance.date} has been {status_display.lower()}"
          
           # Notify student
           Notification.create_notification(
               user=instance.student.user,
               message=message,
               notification_type='absence_excuse_update',
               related_object=instance
           )
          
           # Notify parent if exists
           if instance.student.parent:
               Notification.create_notification(
                   user=instance.student.parent.user,
                   message=f"{instance.student}'s absence excuse has been {status_display.lower()}",
                   notification_type='absence_excuse_update',
                   related_object=instance
               )
           print(f"Status change notifications created for student and parent")  # Debugging
          
   except Exception as e:
       print(f"Error creating absence excuse notifications: {e}")


@receiver(post_save, sender=AcademicPerformance)
def notify_on_new_academic_performance(sender, instance, created, **kwargs):
   if created:
       try:
           # Notify student
           message = f"New grade recorded for {instance.subject}: {instance.grade}"
           Notification.create_notification(
               user=instance.student.user,
               message=message,
               notification_type='new_grade',
               related_object=instance
           )
          
           # Notify parent if exists
           if instance.student.parent:
               Notification.create_notification(
                   user=instance.student.parent.user,
                   message=f"{instance.student} has a new grade in {instance.subject}: {instance.grade}",
                   notification_type='new_grade',
                   related_object=instance
               )
           print("Grade notifications created for student and parent")  # Debugging
       except Exception as e:
           print(f"Error creating grade notifications: {e}")


@receiver(post_save, sender=AssignmentSubmission)
def notify_admin_on_submission(sender, instance, created, **kwargs):
   if created:
       try:
           admin_users = get_user_model().objects.filter(Q(user_type='admin') | Q(is_superuser=True))
           message = f"New submission for {instance.assignment.title} by {instance.student}"
          
           for admin in admin_users.distinct():
               Notification.create_notification(
                   user=admin,
                   message=message,
                   notification_type='assignment_submitted',
                   related_object=instance
               )
           print(f"Notifications created for {admin_users.count()} admins")  # Debugging
       except Exception as e:
           print(f"Error creating submission notifications: {e}")