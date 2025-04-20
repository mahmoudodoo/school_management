// Store chart instances
let attendanceChart = null;


document.addEventListener('DOMContentLoaded', function() {
   // Tab Switching Functionality
   const tabBtns = document.querySelectorAll('.tab-btn');
   const tabContents = document.querySelectorAll('.tab-content');
  
   tabBtns.forEach(btn => {
       btn.addEventListener('click', () => {
           // Remove active class from all buttons and contents
           tabBtns.forEach(b => b.classList.remove('active'));
           tabContents.forEach(c => c.classList.remove('active'));
          
           // Add active class to clicked button and corresponding content
           btn.classList.add('active');
           const tabId = btn.getAttribute('data-tab');
           const tabContent = document.getElementById(`${tabId}-tab`);
           tabContent.classList.add('active');
          
           // If attendance chart exists in the activated tab, render it
           if (tabId === 'performance') {
               renderAttendanceChart();
           }
       });
   });


   // Admin Tab Switching
   const adminTabBtns = document.querySelectorAll('.admin-tab-btn');
   const adminTabContents = document.querySelectorAll('.admin-tab-content');
  
   if (adminTabBtns.length > 0) {
       adminTabBtns.forEach(btn => {
           btn.addEventListener('click', () => {
               adminTabBtns.forEach(b => b.classList.remove('active'));
               adminTabContents.forEach(c => c.classList.remove('active'));
              
               btn.classList.add('active');
               const tabId = btn.getAttribute('data-admin-tab');
               document.getElementById(`admin-${tabId}-tab`).classList.add('active');
           });
       });
   }


   // Assignment Submission Modal Handling
   const submissionModal = document.getElementById('assignment-submission-modal');
   if (submissionModal) {
       const closeModal = submissionModal.querySelector('.close-modal');
      
       // Open modal when assignment submit button is clicked
       document.querySelectorAll('.open-submission-modal').forEach(btn => {
           btn.addEventListener('click', function() {
               const assignmentId = this.getAttribute('data-assignment-id');
               const assignmentTitle = this.getAttribute('data-assignment-title');
               openAssignmentSubmissionModal(assignmentId, assignmentTitle);
           });
       });


       closeModal.addEventListener('click', () => {
           submissionModal.classList.remove('active');
       });


       window.addEventListener('click', (e) => {
           if (e.target === submissionModal) {
               submissionModal.classList.remove('active');
           }
       });


       // Handle assignment submission form
       const assignmentForm = document.getElementById('assignment-submission-form');
       if (assignmentForm) {
           assignmentForm.addEventListener('submit', function(e) {
               e.preventDefault();
               handleAssignmentSubmission(this);
           });
       }
   }


   // Handle absence excuse form submission
   const absenceExcuseForm = document.getElementById('absence-excuse-form');
   if (absenceExcuseForm) {
       absenceExcuseForm.addEventListener('submit', function(e) {
           e.preventDefault();
           handleAbsenceExcuseSubmission(this);
       });
   }


   // Mark Notification as Read
   const markReadBtns = document.querySelectorAll('.mark-read-btn');
   markReadBtns.forEach(btn => {
       btn.addEventListener('click', function() {
           const notificationId = this.getAttribute('data-id');
           markNotificationAsRead(notificationId);
       });
   });


   // Mark All Notifications as Read
   const markAllReadBtn = document.getElementById('mark-all-read');
   if (markAllReadBtn) {
       markAllReadBtn.addEventListener('click', function() {
           markAllNotificationsAsRead();
       });
   }


   // Delete Notification
   const deleteNotificationBtns = document.querySelectorAll('.delete-notification-btn');
   deleteNotificationBtns.forEach(btn => {
       btn.addEventListener('click', function() {
           const notificationId = this.getAttribute('data-id');
           deleteNotification(notificationId);
       });
   });


   // Admin Modal Handling
   if (document.getElementById('admin-modal')) {
       const modal = document.getElementById('admin-modal');
       const closeModal = document.querySelector('.close-modal');
      
       // Add Student/Parent/Performance buttons
       const addButtons = document.querySelectorAll('[id$="-btn"]');
       addButtons.forEach(btn => {
           btn.addEventListener('click', function() {
               const itemType = this.id.replace('-btn', '').replace('add-', '');
               openAdminModal('add', itemType);
           });
       });


       // Edit buttons
       const editButtons = document.querySelectorAll('.edit-btn');
       editButtons.forEach(btn => {
           btn.addEventListener('click', function() {
               const itemId = this.getAttribute('data-id');
               const itemType = this.closest('.admin-tab-content').id.replace('admin-', '').replace('-tab', '');
               openAdminModal('edit', itemType, itemId);
           });
       });


       // Delete buttons
       const deleteButtons = document.querySelectorAll('.delete-btn');
       deleteButtons.forEach(btn => {
           btn.addEventListener('click', function() {
               const itemId = this.getAttribute('data-id');
               const itemType = this.closest('.admin-tab-content').id.replace('admin-', '').replace('-tab', '');
               if (confirm('Are you sure you want to delete this item?')) {
                   deleteItem(itemType, itemId);
               }
           });
       });


       closeModal.addEventListener('click', () => {
           modal.classList.remove('active');
       });


       window.addEventListener('click', (e) => {
           if (e.target === modal) {
               modal.classList.remove('active');
           }
       });
   }


   // Form Submissions
   const personalForm = document.getElementById('personal-form');
   if (personalForm) {
       personalForm.addEventListener('submit', function(e) {
           e.preventDefault();
           updatePersonalInfo(this);
       });
   }


   const passwordForm = document.getElementById('password-form');
   if (passwordForm) {
       passwordForm.addEventListener('submit', function(e) {
           e.preventDefault();
           changePassword(this);
       });
   }


   const notificationForm = document.getElementById('send-notification-form');
   if (notificationForm) {
       notificationForm.addEventListener('submit', function(e) {
           e.preventDefault();
           sendNotification(this);
       });
   }


   const adminForm = document.getElementById('admin-form');
   if (adminForm) {
       adminForm.addEventListener('submit', function(e) {
           e.preventDefault();
           saveAdminItem(this);
       });
   }


   // Render attendance chart if on performance tab
   if (document.getElementById('performance-tab') && document.getElementById('performance-tab').classList.contains('active')) {
       renderAttendanceChart();
   }
});


// Assignment Submission Functions
function openAssignmentSubmissionModal(assignmentId, assignmentTitle) {
   const modal = document.getElementById('assignment-submission-modal');
   const modalTitle = document.getElementById('submission-modal-title');
   const assignmentIdInput = document.getElementById('assignment-id');
  
   modalTitle.textContent = `Submit Assignment: ${assignmentTitle}`;
   assignmentIdInput.value = assignmentId;
   modal.classList.add('active');
}


function handleAssignmentSubmission(form) {
   const formData = new FormData(form);
   const assignmentId = formData.get('assignment_id');
  
   fetch(`/assignments/${assignmentId}/submit/`, {
       method: 'POST',
       body: formData,
       headers: {
           'X-CSRFToken': getCookie('csrftoken')
       }
   })
   .then(response => response.json())
   .then(data => {
       if (data.success) {
           showAlert('Assignment submitted successfully!', 'success');
           document.getElementById('assignment-submission-modal').classList.remove('active');
           location.reload(); // Refresh to show the new submission
       } else {
           showAlert('Error submitting assignment: ' + JSON.stringify(data.error), 'error');
       }
   })
   .catch(error => {
       showAlert('Error submitting assignment: ' + error.message, 'error');
   });
}


// Absence Excuse Functions
function handleAbsenceExcuseSubmission(form) {
   const formData = new FormData(form);
  
   fetch('/absence-excuses/submit/', {
       method: 'POST',
       body: formData,
       headers: {
           'X-CSRFToken': getCookie('csrftoken')
       }
   })
   .then(response => response.json())
   .then(data => {
       if (data.success) {
           showAlert('Absence excuse submitted successfully!', 'success');
           form.reset();
           location.reload(); // Refresh to show the new excuse
       } else {
           showAlert('Error submitting absence excuse: ' + JSON.stringify(data.error), 'error');
       }
   })
   .catch(error => {
       showAlert('Error submitting absence excuse: ' + error.message, 'error');
   });
}


function renderAttendanceChart() {
   const ctx = document.getElementById('attendanceChart');
   if (!ctx) return;
  
   // Destroy existing chart if it exists
   if (attendanceChart) {
       attendanceChart.destroy();
   }
  
   // Use actual data if available, otherwise use empty data
   const chartData = window.attendanceChartData || {
       labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
       present: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       absent: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
   };
  
   // Create new chart instance
   attendanceChart = new Chart(ctx, {
       type: 'bar',
       data: {
           labels: chartData.labels,
           datasets: [
               {
                   label: 'Present',
                   data: chartData.present,
                   backgroundColor: '#4ad66d',
                   borderColor: '#4ad66d',
                   borderWidth: 1
               },
               {
                   label: 'Absent',
                   data: chartData.absent,
                   backgroundColor: '#f72585',
                   borderColor: '#f72585',
                   borderWidth: 1
               }
           ]
       },
       options: {
           responsive: true,
           maintainAspectRatio: false,
           scales: {
               y: {
                   beginAtZero: true,
                   ticks: {
                       stepSize: 1
                   }
               }
           },
           plugins: {
               legend: {
                   position: 'top',
               },
               tooltip: {
                   mode: 'index',
                   intersect: false,
                   callbacks: {
                       label: function(context) {
                           return `${context.dataset.label}: ${context.raw}`;
                       }
                   }
               }
           }
       }
   });
}


// AJAX Functions
function markNotificationAsRead(notificationId) {
   fetch(`/notifications/${notificationId}/mark-read/`, {
       method: 'POST',
       headers: {
           'X-CSRFToken': getCookie('csrftoken'),
           'Content-Type': 'application/json'
       }
   })
   .then(response => response.json())
   .then(data => {
       if (data.success) {
           const notificationCard = document.querySelector(`.notification-card[data-id="${notificationId}"]`);
           notificationCard.classList.remove('unread');
           notificationCard.querySelector('.mark-read-btn').remove();
           updateNotificationBadge();
       }
   });
}


function markAllNotificationsAsRead() {
   fetch('/notifications/mark-all-read/', {
       method: 'POST',
       headers: {
           'X-CSRFToken': getCookie('csrftoken'),
           'Content-Type': 'application/json'
       }
   })
   .then(response => response.json())
   .then(data => {
       if (data.success) {
           document.querySelectorAll('.notification-card.unread').forEach(card => {
               card.classList.remove('unread');
               const markReadBtn = card.querySelector('.mark-read-btn');
               if (markReadBtn) markReadBtn.remove();
           });
           const badge = document.querySelector('.notification-badge');
           if (badge) badge.remove();
       }
   });
}


function deleteNotification(notificationId) {
   fetch(`/notifications/${notificationId}/delete/`, {
       method: 'DELETE',
       headers: {
           'X-CSRFToken': getCookie('csrftoken'),
           'Content-Type': 'application/json'
       }
   })
   .then(response => response.json())
   .then(data => {
       if (data.success) {
           document.querySelector(`.notification-card[data-id="${notificationId}"]`).remove();
           updateNotificationBadge();
           if (document.querySelectorAll('.notification-card').length === 0) {
               const notificationsList = document.querySelector('.notifications-list');
               notificationsList.innerHTML = `
                   <div class="empty-state">
                       <span class="material-symbols-outlined">notifications_off</span>
                       <p>No notifications yet</p>
                   </div>`;
           }
       }
   });
}


function updatePersonalInfo(form) {
   const formData = new FormData(form);
   fetch('/profile/update/', {
       method: 'POST',
       body: formData,
       headers: {
           'X-CSRFToken': getCookie('csrftoken')
       }
   })
   .then(response => response.json())
   .then(data => {
       if (data.success) {
           showAlert('Personal information updated successfully!', 'success');
       } else {
           showAlert('Error updating personal information: ' + data.error, 'error');
       }
   });
}


function changePassword(form) {
   const formData = new FormData(form);
   fetch('/profile/change-password/', {
       method: 'POST',
       body: formData,
       headers: {
           'X-CSRFToken': getCookie('csrftoken')
       }
   })
   .then(response => response.json())
   .then(data => {
       if (data.success) {
           showAlert('Password changed successfully!', 'success');
           form.reset();
       } else {
           showAlert('Error changing password: ' + data.error, 'error');
       }
   });
}


function sendNotification(form) {
   const formData = new FormData(form);
   fetch('/notifications/send/', {
       method: 'POST',
       body: formData,
       headers: {
           'X-CSRFToken': getCookie('csrftoken')
       }
   })
   .then(response => response.json())
   .then(data => {
       if (data.success) {
           showAlert('Notification sent successfully!', 'success');
           form.reset();
           const notificationsList = document.querySelector('.notifications-list');
           const emptyState = notificationsList.querySelector('.empty-state');
          
           if (emptyState) emptyState.remove();
          
           const now = new Date();
           const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          
           notificationsList.insertAdjacentHTML('afterbegin', `
               <div class="notification-card unread" data-id="${data.notification_id}">
                   <div class="notification-content">
                       <p>${formData.get('message')}</p>
                       <small>Just now</small>
                   </div>
                   <div class="notification-actions">
                       <button class="mark-read-btn" data-id="${data.notification_id}">
                           <span class="material-symbols-outlined">check</span>
                       </button>
                       <button class="delete-notification-btn" data-id="${data.notification_id}">
                           <span class="material-symbols-outlined">delete</span>
                       </button>
                   </div>
               </div>`);
          
           document.querySelector(`.mark-read-btn[data-id="${data.notification_id}"]`)
               .addEventListener('click', function() {
                   markNotificationAsRead(data.notification_id);
               });
          
           document.querySelector(`.delete-notification-btn[data-id="${data.notification_id}"]`)
               .addEventListener('click', function() {
                   deleteNotification(data.notification_id);
               });
          
           updateNotificationBadge();
       } else {
           showAlert('Error sending notification: ' + data.error, 'error');
       }
   });
}


function openAdminModal(action, itemType, itemId = null) {
   const modal = document.getElementById('admin-modal');
   const modalTitle = document.getElementById('modal-title');
   const formFields = document.getElementById('form-fields');
   const itemIdInput = document.getElementById('item-id');
   const itemTypeInput = document.getElementById('item-type');
  
   modalTitle.textContent = `${action === 'add' ? 'Add New' : 'Edit'} ${itemType.charAt(0).toUpperCase() + itemType.slice(1)}`;
   itemIdInput.value = itemId || '';
   itemTypeInput.value = itemType;
  
   let fieldsHtml = '';
  
   if (itemType === 'student') {
       const parents = window.allParents || [];
       const users = window.allUsers || [];
       fieldsHtml = `
           <div class="form-group">
               <label for="user">Select Student User</label>
               <select id="user" name="user" required>
                   <option value="">Select a student user</option>
                   ${users.filter(u => u.user_type === 'student' && !u.student_profile).map(u => `
                       <option value="${u.id}">${u.username} (${u.get_full_name || 'No name'})</option>
                   `).join('')}
               </select>
           </div>
           <div class="form-group">
               <label for="first_name">First Name</label>
               <input type="text" id="first_name" name="first_name" required>
           </div>
           <div class="form-group">
               <label for="last_name">Last Name</label>
               <input type="text" id="last_name" name="last_name" required>
           </div>
           <div class="form-group">
               <label for="date_of_birth">Date of Birth</label>
               <input type="date" id="date_of_birth" name="date_of_birth" required>
           </div>
           <div class="form-group">
               <label for="parent">Parent (Optional)</label>
               <select id="parent" name="parent">
                   <option value="">Select a parent (optional)</option>
                   ${parents.map(p => `<option value="${p.id}">${p.user.get_full_name || p.user.username}</option>`).join('')}
               </select>
           </div>
           <div class="form-group">
               <label for="absence_limit">Absence Limit</label>
               <input type="number" id="absence_limit" name="absence_limit" value="10" min="1" required>
           </div>`;
   } else if (itemType === 'parent') {
       const users = window.allUsers || [];
       fieldsHtml = `
           <div class="form-group">
               <label for="user">Select Parent User</label>
               <select id="user" name="user" required>
                   <option value="">Select a parent user</option>
                   ${users.filter(u => u.user_type === 'parent' && !u.parent_profile).map(u => `
                       <option value="${u.id}">${u.username} (${u.get_full_name || 'No name'})</option>
                   `).join('')}
               </select>
           </div>
           <div class="form-group">
               <label for="address">Address</label>
               <input type="text" id="address" name="address">
           </div>`;
   } else if (itemType === 'performance') {
       const students = window.allStudents || [];
       const subjects = window.allSubjects || [];
       fieldsHtml = `
           <div class="form-group">
               <label for="student">Student</label>
               <select id="student" name="student" required>
                   <option value="">Select a student</option>
                   ${students.map(s => `<option value="${s.id}">${s.first_name} ${s.last_name}</option>`).join('')}
               </select>
           </div>
           <div class="form-group">
               <label for="subject">Subject</label>
               <select id="subject" name="subject" required>
                   <option value="">Select a subject</option>
                   ${subjects.map(s => `<option value="${s.id}">${s.name}</option>`).join('')}
               </select>
           </div>
           <div class="form-group">
               <label for="grade">Grade</label>
               <select id="grade" name="grade" required>
                   <option value="">Select a grade</option>
                   <option value="A+">A+</option>
                   <option value="A">A</option>
                   <option value="B">B</option>
                   <option value="C">C</option>
                   <option value="D">D</option>
                   <option value="F">F</option>
               </select>
           </div>`;
   }
  
   formFields.innerHTML = fieldsHtml;
  
   if (action === 'edit' && itemId) {
       fetch(`/manage/get-${itemType}/${itemId}/`)
       .then(response => response.json())
       .then(data => {
           if (data.success) {
               const itemData = data.item;
               for (const field in itemData) {
                   const input = document.querySelector(`[name="${field}"]`);
                   if (input) {
                       input.value = itemData[field];
                   }
               }
           }
       });
   }
  
   modal.classList.add('active');
}


function saveAdminItem(form) {
   const formData = new FormData(form);
   const itemType = formData.get('item_type');
   const itemId = formData.get('item_id');
  
   const url = itemId ? `/manage/update-${itemType}/${itemId}/` : `/manage/add-${itemType}/`;
  
   if (itemType === 'performance') {
       if (!formData.get('student') || !formData.get('subject') || !formData.get('grade')) {
           showAlert('Please fill all required fields', 'error');
           return;
       }
   }
  
   fetch(url, {
       method: 'POST',
       body: formData,
       headers: {
           'X-CSRFToken': getCookie('csrftoken'),
       }
   })
   .then(response => {
       if (!response.ok) {
           return response.json().then(err => {
               throw new Error(err.error || 'Request failed');
           });
       }
       return response.json();
   })
   .then(data => {
       if (data.success) {
           showAlert(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} ${itemId ? 'updated' : 'added'} successfully!`, 'success');
           document.getElementById('admin-modal').classList.remove('active');
           if (itemType === 'performance') {
               updatePerformanceTable(data.performance_id || itemId, formData, itemId ? 'update' : 'add');
           } else {
               location.reload();
           }
       } else {
           showAlert(`Error: ${data.error}`, 'error');
       }
   })
   .catch(error => {
       console.error('Error:', error);
       showAlert(`Error: ${error.message}`, 'error');
   });
}


function updatePerformanceTable(performanceId, formData, action) {
   const studentSelect = document.getElementById('student');
   const subjectSelect = document.getElementById('subject');
   const grade = formData.get('grade');
  
   const studentName = studentSelect ? studentSelect.options[studentSelect.selectedIndex].text : '';
   const subjectName = subjectSelect ? subjectSelect.options[subjectSelect.selectedIndex].text : '';
  
   const isFailing = ['F', 'D'].includes(grade);
   const isExcelling = ['A', 'A+'].includes(grade);
  
   if (action === 'add') {
       const tableBody = document.querySelector('#admin-performance-tab tbody');
       const newRow = document.createElement('tr');
       newRow.className = isFailing ? 'failing' : isExcelling ? 'excelling' : '';
       newRow.innerHTML = `
           <td>${studentName}</td>
           <td>${subjectName}</td>
           <td>${grade}</td>
           <td>
               ${isFailing ? '<span class="status-badge failing">Failing</span>' :
                isExcelling ? '<span class="status-badge excelling">Excelling</span>' :
                '<span class="status-badge">Satisfactory</span>'}
           </td>
           <td class="actions">
               <button class="edit-btn" data-id="${performanceId}">
                   <span class="material-symbols-outlined">edit</span>
               </button>
               <button class="delete-btn" data-id="${performanceId}">
                   <span class="material-symbols-outlined">delete</span>
               </button>
           </td>`;
      
       newRow.querySelector('.edit-btn').addEventListener('click', function() {
           openAdminModal('edit', 'performance', performanceId);
       });
      
       newRow.querySelector('.delete-btn').addEventListener('click', function() {
           if (confirm('Are you sure you want to delete this performance record?')) {
               deleteItem('performance', performanceId);
           }
       });
      
       tableBody.appendChild(newRow);
      
       const emptyRow = tableBody.querySelector('tr td[colspan="5"]');
       if (emptyRow) {
           emptyRow.closest('tr').remove();
       }
   } else {
       const row = document.querySelector(`tr[data-id="${performanceId}"]`) ||
                  document.querySelector(`.edit-btn[data-id="${performanceId}"]`)?.closest('tr');
      
       if (row) {
           row.className = isFailing ? 'failing' : isExcelling ? 'excelling' : '';
           row.cells[0].textContent = studentName;
           row.cells[1].textContent = subjectName;
           row.cells[2].textContent = grade;
           row.cells[3].innerHTML = isFailing ? '<span class="status-badge failing">Failing</span>' :
                                     isExcelling ? '<span class="status-badge excelling">Excelling</span>' :
                                     '<span class="status-badge">Satisfactory</span>';
       }
   }
  
   document.getElementById('admin-modal').classList.remove('active');
}


function deleteItem(itemType, itemId) {
   fetch(`/manage/delete-${itemType}/${itemId}/`, {
       method: 'DELETE',
       headers: {
           'X-CSRFToken': getCookie('csrftoken'),
           'Content-Type': 'application/json'
       }
   })
   .then(response => response.json())
   .then(data => {
       if (data.success) {
           showAlert(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} deleted successfully!`, 'success');
           location.reload();
       } else {
           showAlert(`Error deleting ${itemType}: ${data.error}`, 'error');
       }
   });
}


// Helper Functions
function getCookie(name) {
   let cookieValue = null;
   if (document.cookie && document.cookie !== '') {
       const cookies = document.cookie.split(';');
       for (let i = 0; i < cookies.length; i++) {
           const cookie = cookies[i].trim();
           if (cookie.substring(0, name.length + 1) === (name + '=')) {
               cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
               break;
           }
       }
   }
   return cookieValue;
}


function showAlert(message, type) {
   const alert = document.createElement('div');
   alert.className = `alert alert-${type}`;
   alert.textContent = message;
   alert.style.position = 'fixed';
   alert.style.top = '20px';
   alert.style.right = '20px';
   alert.style.padding = '1rem 1.5rem';
   alert.style.borderRadius = 'var(--border-radius)';
   alert.style.backgroundColor = type === 'success' ? 'var(--success-color)' : 'var(--danger-color)';
   alert.style.color = 'white';
   alert.style.boxShadow = 'var(--shadow)';
   alert.style.zIndex = '1000';
   alert.style.animation = 'fadeIn 0.3s ease';
  
   document.body.appendChild(alert);
  
   setTimeout(() => {
       alert.style.animation = 'fadeOut 0.3s ease';
       setTimeout(() => {
           alert.remove();
       }, 300);
   }, 3000);
}


function updateNotificationBadge() {
   const unreadCount = document.querySelectorAll('.notification-card.unread').length;
   const badge = document.querySelector('.notification-badge');
   const tabBtn = document.querySelector('.tab-btn[data-tab="notifications"]');
  
   if (unreadCount > 0) {
       if (badge) {
           badge.textContent = unreadCount;
       } else {
           const newBadge = document.createElement('span');
           newBadge.className = 'notification-badge';
           newBadge.textContent = unreadCount;
           tabBtn.appendChild(newBadge);
       }
   } else if (badge) {
       badge.remove();
   }
}
