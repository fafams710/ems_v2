from django.contrib import admin
from .models import AuthCode
from .models import LeaveRequest, EmployeeProfile

class AuthCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'is_active', 'created_at']  # Correctly reference the fields
    list_filter = ['is_active', 'created_at']  # These fields now exist in the model


admin.site.register(AuthCode, AuthCodeAdmin)
admin.site.register(LeaveRequest)
admin.site.register(EmployeeProfile)