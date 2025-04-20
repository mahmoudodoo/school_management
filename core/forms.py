# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm, PasswordChangeForm
from .models import User
from django.core.exceptions import ValidationError
from .models import User, Parent, Student,AssignmentSubmission,AbsenceExcuse




class CustomUserCreationForm(UserCreationForm):
   email = forms.EmailField(
       required=True,
       widget=forms.EmailInput(attrs={
           'autocomplete': 'email',
           'placeholder': 'your@email.com'
       })
   )
   phone_number = forms.CharField(
       required=False,
       widget=forms.TextInput(attrs={
           'placeholder': '+1234567890'
       })
   )
   user_type = forms.ChoiceField(
       choices=User.USER_TYPE_CHOICES,
       widget=forms.Select(attrs={
           'class': 'select-field'
       })
   )


   class Meta:
       model = User
       fields = ('username', 'email', 'phone_number', 'user_type', 'password1', 'password2')


   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       # Add placeholders for password fields
       self.fields['password1'].widget.attrs.update({'placeholder': 'Enter password'})
       self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password'})
      
       for field_name, field in self.fields.items():
           field.widget.attrs.update({
               'class': 'input-field',
               'data-validate': str(field.required).lower()
           })


   def save(self, commit=True):
       user = super().save(commit=False)
       user.email = self.cleaned_data['email']
       user.phone_number = self.cleaned_data['phone_number']
       user.user_type = self.cleaned_data['user_type']
      
       if commit:
           user.save()
       return user
  
  
class UserUpdateForm(UserChangeForm):
   class Meta:
       model = User
       fields = ('first_name', 'last_name', 'email', 'phone_number')


   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.fields.pop('password')  # Remove password field


class ParentUpdateForm(forms.ModelForm):
   class Meta:
       model = Parent
       fields = ('address',)


class StudentUpdateForm(forms.ModelForm):
   class Meta:
       model = Student
       fields = ('first_name', 'last_name', 'date_of_birth', 'absence_limit')
       widgets = {
           'date_of_birth': forms.DateInput(attrs={'type': 'date'})
       }
      
      
# Add these forms to forms.py
class AssignmentSubmissionForm(forms.ModelForm):
   class Meta:
       model = AssignmentSubmission
       fields = ('submission_file', 'notes')
       widgets = {
           'notes': forms.Textarea(attrs={'rows': 3}),
       }


class AbsenceExcuseForm(forms.ModelForm):
   class Meta:
       model = AbsenceExcuse
       fields = ('date', 'reason', 'supporting_document')
       widgets = {
           'date': forms.DateInput(attrs={'type': 'date'}),
           'reason': forms.Textarea(attrs={'rows': 3}),
       }
