from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import CustomUserCreationForm, UserUpdateForm, ParentUpdateForm, StudentUpdateForm
from .models import User, Parent, Student, Attendance, AcademicPerformance, Notification, Subject
from django.contrib import messages
from django.forms.models import model_to_dict
from django.db.models import Prefetch, Q  # Add this import


def home(request):
   return render(request, 'home.html')


def register(request):
   if request.user.is_authenticated:
       return redirect('home')
  
   if request.method == 'POST':
       form = CustomUserCreationForm(request.POST)
       if form.is_valid():
           user = form.save()
           login(request, user)
           return redirect('home')
       else:
           print(form.errors)
   else:
       form = CustomUserCreationForm()
   return render(request, 'register.html', {'form': form})


def user_login(request):
   if request.user.is_authenticated:
       return redirect('home')
  
   if request.method == 'POST':
       form = AuthenticationForm(request, data=request.POST)
       if form.is_valid():
           user = form.get_user()
           login(request, user)
           return redirect('home')
   else:
       form = AuthenticationForm()
   return render(request, 'login.html', {'form': form})


def user_logout(request):
   logout(request)
   return redirect('home')


@login_required
def profile(request):
   context = {}
  
   # Basic user context
   context['user'] = request.user
  
   # Parent-specific context
   if request.user.user_type == 'parent':
       try:
           parent_profile = request.user.parent_profile
           context['parent_profile'] = parent_profile
          
           # Get children with attendance counts and prefetch related data
           children = parent_profile.students.all().prefetch_related(
               Prefetch('attendances', queryset=Attendance.objects.order_by('-date')),
               Prefetch('academic_performances',
                       queryset=AcademicPerformance.objects.select_related('subject')
                       .order_by('subject__name'))
           )
          
           for child in children:
               child.absent_count = child.attendances.filter(status='Absent').count()
               child.present_count = child.attendances.filter(status='Present').count()
              
               # Prepare performance data by subject for each child
               child.performance_by_subject = {
                   perf.subject.name: perf.grade
                   for perf in child.academic_performances.all()
               }
              
           context['children'] = children
          
       except Parent.DoesNotExist:
           messages.warning(request, "Parent profile not found. Please contact admin.")
  
   # Student-specific context
   elif request.user.user_type == 'student':
       try:
           student_profile = request.user.student_profile
           context['student_profile'] = student_profile
          
           # Attendance data with monthly breakdown
           attendances = student_profile.attendances.all().order_by('date')
           context['attendances'] = attendances
           context['present_count'] = present_count = attendances.filter(status='Present').count()
           context['absent_count'] = absent_count = attendances.filter(status='Absent').count()
          
           # Prepare monthly attendance data for chart
           monthly_counts = {}
           for month in range(1, 13):
               monthly_counts[month] = {
                   'present': attendances.filter(
                       status='Present',
                       date__month=month
                   ).count(),
                   'absent': attendances.filter(
                       status='Absent',
                       date__month=month
                   ).count()
               }
          
           context['attendance_chart_data'] = {
               'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
               'present': [monthly_counts[m]['present'] for m in range(1, 13)],
               'absent': [monthly_counts[m]['absent'] for m in range(1, 13)],
               'total_present': present_count,
               'total_absent': absent_count
           }
          
           # Performance data with subject details
           performances = student_profile.academic_performances.all() \
               .select_related('subject') \
               .order_by('subject__name')
           context['performances'] = performances
          
           # Calculate grades summary
           grade_counts = {
               'A+': performances.filter(grade='A+').count(),
               'A': performances.filter(grade='A').count(),
               'B': performances.filter(grade='B').count(),
               'C': performances.filter(grade='C').count(),
               'D': performances.filter(grade='D').count(),
               'F': performances.filter(grade='F').count()
           }
           context['grade_counts'] = grade_counts
          
           # Prepare performance data for charts
           context['performance_chart_data'] = {
               'subjects': [p.subject.name for p in performances],
               'grades': [p.grade for p in performances],
               'is_failing': [p.is_failing() for p in performances],
               'is_excelling': [p.is_excelling() for p in performances]
           }
          
       except Student.DoesNotExist:
           messages.warning(request, "Student profile not found. Please contact admin.")
  
   # Admin-specific context
   if request.user.is_superuser:
       # Students data with attendance counts
       students = Student.objects.all() \
           .select_related('user', 'parent__user') \
           .prefetch_related('attendances') \
           .order_by('last_name', 'first_name')
      
       for student in students:
           student.absent_count = student.attendances.filter(status='Absent').count()
           student.present_count = student.attendances.filter(status='Present').count()
       context['all_students'] = students
      
       # Parents data with student counts
       parents = Parent.objects.all() \
           .select_related('user') \
           .prefetch_related('students') \
           .order_by('user__last_name', 'user__first_name')
      
       for parent in parents:
           parent.student_count = parent.students.count()
       context['all_parents'] = parents
      
       # Academic performances with related data
       performances = AcademicPerformance.objects.all() \
           .select_related('student', 'subject') \
           .order_by('student__last_name', 'student__first_name', 'subject__name')
       context['all_performances'] = performances
      
       # Subjects ordered by name
       context['all_subjects'] = Subject.objects.all().order_by('name')
      
       # All users (for parent/student creation)
       context['all_users'] = User.objects.filter(
           Q(user_type='student') | Q(user_type='parent')
       ).order_by('last_name', 'first_name')
      
       # School-wide attendance data for admin dashboard
       context['attendance_data'] = {
           'labels': ['Present', 'Absent'],
           'data': [
               Attendance.objects.filter(status='Present').count(),
               Attendance.objects.filter(status='Absent').count()
           ]
       }
  
   # Notifications data
   context['unread_notifications_count'] = request.user.notifications.filter(
       is_read=False
   ).count()
  
   # Recent notifications (last 5)
   context['recent_notifications'] = request.user.notifications.all() \
       .order_by('-timestamp')[:5]
  
   return render(request, 'profile.html', context)




@login_required
def update_profile(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'personal':
            user_form = UserUpdateForm(request.POST, instance=request.user)
            
            # Initialize profile_form as None by default
            profile_form = None
            
            # Only try to get profile forms if user is parent or student
            if request.user.user_type == 'parent':
                try:
                    profile_form = ParentUpdateForm(request.POST, instance=request.user.parent_profile)
                except Parent.DoesNotExist:
                    pass  # Admin or user without parent profile
            elif request.user.user_type == 'student':
                try:
                    profile_form = StudentUpdateForm(request.POST, instance=request.user.student_profile)
                except Student.DoesNotExist:
                    pass  # Admin or user without student profile
            
            # Validate forms (only profile_form if it exists)
            if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
                user_form.save()
                if profile_form:
                    profile_form.save()
                return JsonResponse({'success': True})
            else:
                errors = {}
                if user_form.errors:
                    errors.update(user_form.errors.get_json_data())
                if profile_form and profile_form.errors:
                    errors.update(profile_form.errors.get_json_data())
                return JsonResponse({'success': False, 'error': errors})
        
        elif form_type == 'password':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': form.errors.get_json_data()})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def mark_notification_read(request, notification_id):
   if request.method == 'POST':
       try:
           notification = request.user.notifications.get(id=notification_id)
           notification.is_read = True
           notification.save()
           return JsonResponse({'success': True})
       except Notification.DoesNotExist:
           return JsonResponse({'success': False, 'error': 'Notification not found'})
   return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def mark_all_notifications_read(request):
   if request.method == 'POST':
       request.user.notifications.filter(is_read=False).update(is_read=True)
       return JsonResponse({'success': True})
   return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def delete_notification(request, notification_id):
   if request.method == 'DELETE':
       try:
           notification = request.user.notifications.get(id=notification_id)
           notification.delete()
           return JsonResponse({'success': True})
       except Notification.DoesNotExist:
           return JsonResponse({'success': False, 'error': 'Notification not found'})
   return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def send_notification(request):
   if request.method == 'POST' and request.user.is_superuser:
       recipient_id = request.POST.get('recipient')
       message = request.POST.get('message')
      
       try:
           recipient = User.objects.get(id=recipient_id)
           notification = Notification.objects.create(
               user=recipient,
               message=message
           )
           return JsonResponse({'success': True, 'notification_id': notification.id})
       except User.DoesNotExist:
           return JsonResponse({'success': False, 'error': 'Recipient not found'})
   return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def get_admin_item(request, item_type, item_id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        if item_type == 'student':
            item = Student.objects.get(id=item_id)
            data = {
                'user_id': item.user.id,
                'first_name': item.first_name,
                'last_name': item.last_name,
                'date_of_birth': item.date_of_birth.strftime('%Y-%m-%d'),
                'parent': item.parent.id if item.parent else '',
                'absence_limit': item.absence_limit
            }
        elif item_type == 'parent':
            item = Parent.objects.get(id=item_id)
            data = {
                'user_id': item.user.id,
                'username': item.user.username,
                'email': item.user.email,
                'first_name': item.user.first_name,
                'last_name': item.user.last_name,
                'phone_number': item.user.phone_number,
                'address': item.address
            }
        elif item_type == 'performance':
            item = AcademicPerformance.objects.get(id=item_id)
            data = {
                'student': item.student.id,
                'subject': item.subject.id,
                'grade': item.grade
            }
        else:
            print(f"Invalid item type received: {item_type}")
            return JsonResponse({'success': False, 'error': 'Invalid item type'})
        
        return JsonResponse({'success': True, 'item': data})
    except Exception as e:
        print(f"Error getting admin item: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})
    
    
@login_required
def add_admin_item(request, item_type):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    if request.method == 'POST':
        try:
            if item_type == 'student':
                user_id = request.POST.get('user')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                date_of_birth = request.POST.get('date_of_birth')
                parent_id = request.POST.get('parent')
                absence_limit = request.POST.get('absence_limit', 10)
                
                if not all([user_id, first_name, last_name, date_of_birth]):
                    return JsonResponse({'success': False, 'error': 'All fields are required'})
                
                try:
                    user = User.objects.get(id=user_id, user_type='student')
                    parent = Parent.objects.get(id=parent_id) if parent_id else None
                    
                    student = Student.objects.create(
                        user=user,
                        first_name=first_name,
                        last_name=last_name,
                        date_of_birth=date_of_birth,
                        parent=parent,
                        absence_limit=absence_limit
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'student_id': student.id
                    })
                    
                except User.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Student user not found'})
                except Parent.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Parent not found'})
                
            elif item_type == 'parent':
                user_id = request.POST.get('user')
                address = request.POST.get('address', '')
                
                if not user_id:
                    return JsonResponse({'success': False, 'error': 'User is required'})
                
                try:
                    user = User.objects.get(id=user_id, user_type='parent')
                    parent = Parent.objects.create(
                        user=user,
                        address=address
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'parent_id': parent.id
                    })
                    
                except User.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Parent user not found'})
                
            elif item_type == 'performance':
                student_id = request.POST.get('student')
                subject_id = request.POST.get('subject')
                grade = request.POST.get('grade')
                
                if not all([student_id, subject_id, grade]):
                    return JsonResponse({'success': False, 'error': 'All fields are required'})
                
                try:
                    student = Student.objects.get(id=student_id)
                    subject = Subject.objects.get(id=subject_id)
                    
                    # Check if performance record already exists for this student and subject
                    if AcademicPerformance.objects.filter(student=student, subject=subject).exists():
                        return JsonResponse({
                            'success': False,
                            'error': 'Performance record already exists for this student and subject'
                        })
                    
                    # Create new performance record
                    performance = AcademicPerformance.objects.create(
                        student=student,
                        subject=subject,
                        grade=grade
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'performance_id': performance.id
                    })
                    
                except Student.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Student not found'})
                except Subject.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Subject not found'})
                
            else:
                return JsonResponse({'success': False, 'error': 'Invalid item type'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def update_admin_item(request, item_type, item_id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    if request.method == 'POST':
        try:
            if item_type == 'student':
                student = Student.objects.get(id=item_id)
                student.first_name = request.POST.get('first_name')
                student.last_name = request.POST.get('last_name')
                student.date_of_birth = request.POST.get('date_of_birth')
                
                parent_id = request.POST.get('parent')
                if parent_id:
                    student.parent = Parent.objects.get(id=parent_id)
                else:
                    student.parent = None
                
                student.absence_limit = request.POST.get('absence_limit', 10)
                student.save()
                
                # Update user info
                user = student.user
                user.first_name = student.first_name
                user.last_name = student.last_name
                user.save()
                
            elif item_type == 'parent':
                parent = Parent.objects.get(id=item_id)
                user = parent.user
                
                user.username = request.POST.get('username')
                user.email = request.POST.get('email')
                user.first_name = request.POST.get('first_name', '')
                user.last_name = request.POST.get('last_name', '')
                user.phone_number = request.POST.get('phone_number', '')
                
                password = request.POST.get('password')
                if password:
                    user.set_password(password)
                
                user.save()
                
                parent.address = request.POST.get('address', '')
                parent.save()
                
            elif item_type == 'performance':
                performance = AcademicPerformance.objects.get(id=item_id)
                performance.student = Student.objects.get(id=request.POST.get('student'))
                performance.subject = Subject.objects.get(id=request.POST.get('subject'))
                performance.grade = request.POST.get('grade')
                performance.save()
            else:
                return JsonResponse({'success': False, 'error': 'Invalid item type'})
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def delete_admin_item(request, item_type, item_id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    if request.method == 'DELETE':
        try:
            if item_type == 'student':
                student = Student.objects.get(id=item_id)
                user = student.user
                student.delete()
                if user:
                    user.delete()
            elif item_type == 'parent':
                parent = Parent.objects.get(id=item_id)
                user = parent.user
                parent.delete()
                if user:
                    user.delete()
            elif item_type == 'performance':
                performance = AcademicPerformance.objects.get(id=item_id)
                performance.delete()
            else:
                print(f"Invalid item type received for deletion: {item_type}")
                return JsonResponse({'success': False, 'error': 'Invalid item type'})
            
            return JsonResponse({'success': True})
        except Exception as e:
            print(f"Error deleting item: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    print("Invalid request method for deletion")
    return JsonResponse({'success': False, 'error': 'Invalid request'})