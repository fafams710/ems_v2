from django.contrib import admin
from .models import Employee
from .forms import EmployeeForm

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'department', 'hire_date', 'salary', 'status', 'role')
    search_fields = ('first_name', 'last_name', 'email', 'department')
    list_filter = ('department', 'role', 'status')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


