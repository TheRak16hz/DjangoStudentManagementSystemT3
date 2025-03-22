from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import Staff

# class StaffBackend(BaseBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             staff = Staff.objects.get(user=username)
#             if check_password(password, staff.password):
#                 return staff
#         except Staff.DoesNotExist:
#             return None

#     def get_user(self, staff_id):
#         try:
#             return Staff.objects.get(pk=staff_id)
#         except Staff.DoesNotExist:
#             return None
