from django.urls import path
from . import views


urlpatterns = [
   path('register/', views.register, name='register'),
   path('login/', views.user_login, name='login'),
   path('logout/', views.user_logout, name='logout'),
   path('', views.profile, name='profile'),
  
   # Profile update endpoints
   path('profile/update/', views.update_profile, name='update_profile'),
   path('profile/change-password/', views.update_profile, name='change_password'),
  
   # Notification endpoints
   path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
   path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
   path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
   path('notifications/send/', views.send_notification, name='send_notification'),
  
   # Admin endpoints - changed from 'admin/' to 'manage/'
   path('manage/get-<str:item_type>/<int:item_id>/', views.get_admin_item, name='get_admin_item'),
   path('manage/add-<str:item_type>/', views.add_admin_item, name='add_admin_item'),
   path('manage/update-<str:item_type>/<int:item_id>/', views.update_admin_item, name='update_admin_item'),
   path('manage/delete-<str:item_type>/<int:item_id>/', views.delete_admin_item, name='delete_admin_item'),
  
   # Add these URLs to urlpatterns
   path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
   path('absence-excuses/submit/', views.submit_absence_excuse, name='submit_absence_excuse'),
]
