from django.contrib.admin import AdminSite


class CustomAdminSite(AdminSite):
   site_header = "School Academic Administration"
   site_title = "School Academic Administration"
   index_title = "Welcome to Administration Portal"


custom_admin_site = CustomAdminSite(name='custom_admin')