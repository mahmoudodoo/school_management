#/create_demo_data.py
import os
import django
from django.contrib.auth.hashers import make_password
from faker import Faker
import random
from datetime import datetime, timedelta


# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()


from core.models import (
   User, Parent, Student, Attendance,
   Subject, AcademicPerformance, Notification, Report
)


fake = Faker()


def create_admin_users():
   print("Creating admin users...")
   for i in range(1, 4):
       username = f'admin{i}'
       email = f'admin{i}@school.com'
       User.objects.create_superuser(
           username=username,
           email=email,
           password='123456',
           first_name=fake.first_name(),
           last_name=fake.last_name(),
           phone_number=fake.phone_number()[:15],
           user_type='parent'  # Admins are technically parents in this system
       )
   print("Created 3 admin users")


def create_parents(num_parents=20):
   print(f"Creating {num_parents} parents...")
   for _ in range(num_parents):
       first_name = fake.first_name()
       last_name = fake.last_name()
       username = f"{first_name.lower()}{last_name.lower()}"
       email = f"{username}@example.com"
      
       user = User.objects.create_user(
           username=username,
           email=email,
           password='123456',
           first_name=first_name,
           last_name=last_name,
           phone_number=fake.phone_number()[:15],
           user_type='parent'
       )
      
       Parent.objects.create(
           user=user,
           address=fake.address()
       )
   print(f"Created {num_parents} parents")


def create_students(num_students=50):
   print(f"Creating {num_students} students...")
   parents = list(Parent.objects.all())
  
   for _ in range(num_students):
       first_name = fake.first_name()
       last_name = fake.last_name()
       username = f"{first_name.lower()}{last_name.lower()}"
       email = f"{username}@student.com"
      
       user = User.objects.create_user(
           username=username,
           email=email,
           password='123456',
           first_name=first_name,
           last_name=last_name,
           phone_number=fake.phone_number()[:15],
           user_type='student'
       )
      
       # Random parent or None
       parent = random.choice(parents) if parents and random.random() > 0.1 else None
      
       # Generate date of birth between 5 and 18 years ago
       dob = fake.date_of_birth(minimum_age=5, maximum_age=18)
      
       Student.objects.create(
           user=user,
           parent=parent,
           first_name=first_name,
           last_name=last_name,
           date_of_birth=dob,
           absence_limit=random.choice([5, 10, 15])
       )
   print(f"Created {num_students} students")


def create_subjects():
   print("Creating subjects...")
   subjects = [
       'Mathematics', 'English', 'Science', 'History', 'Geography',
       'Physics', 'Chemistry', 'Biology', 'Art', 'Music',
       'Physical Education', 'Computer Science', 'Literature', 'Economics'
   ]
  
   for subject in subjects:
       Subject.objects.get_or_create(name=subject)
   print(f"Created {len(subjects)} subjects")


def create_attendances():
   print("Creating attendance records...")
   students = Student.objects.all()
   start_date = datetime.now() - timedelta(days=90)  # Last 90 days
  
   for student in students:
       # Create attendance for random days
       for _ in range(random.randint(10, 30)):
           date = fake.date_between(start_date=start_date, end_date='today')
           status = random.choices(['Present', 'Absent'], weights=[0.85, 0.15])[0]
          
           Attendance.objects.get_or_create(
               student=student,
               date=date,
               defaults={'status': status}
           )
   print(f"Created attendance records for {students.count()} students")


def create_academic_performances():
   print("Creating academic performance records...")
   students = Student.objects.all()
   subjects = Subject.objects.all()
   grades = ['A+', 'A', 'B', 'C', 'D', 'F']
  
   for student in students:
       for subject in subjects:
           # Not all students have grades in all subjects
           if random.random() > 0.3:
               AcademicPerformance.objects.create(
                   student=student,
                   subject=subject,
                   grade=random.choice(grades))
   print("Created academic performance records")


def create_notifications():
   print("Creating notifications...")
   users = User.objects.all()
  
   for user in users:
       # Create between 1-5 notifications per user
       for _ in range(random.randint(1, 5)):
           Notification.objects.create(
               user=user,
               message=fake.sentence(),
               is_read=random.choice([True, False])
           )
   print("Created notifications")


def create_reports():
   print("Creating reports...")
   students = Student.objects.all()
   report_types = ['Attendance', 'Performance']
  
   for student in students:
       # Create 1-3 reports per student
       for _ in range(random.randint(1, 3)):
           report_type = random.choice(report_types)
           if report_type == 'Attendance':
               content = f"Attendance report for {student}. Absences: {student.attendances.filter(status='Absent').count()}"
           else:
               content = f"Performance report for {student}. Subjects: {student.academic_performances.count()}"
          
           Report.objects.create(
               student=student,
               report_type=report_type,
               content=content
           )
   print("Created reports")


def main():
   print("Starting to create demo data...")
  
   # Clear existing data (optional - be careful with this in production!)
   # print("Clearing existing data...")
   # User.objects.all().delete()
   # Subject.objects.all().delete()
  
   create_admin_users()
   create_parents()
   create_students()
   create_subjects()
   create_attendances()
   create_academic_performances()
   create_notifications()
   create_reports()
  
   print("Demo data creation complete!")


if __name__ == '__main__':
   main()