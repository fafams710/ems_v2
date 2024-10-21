from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee
from .forms import EmployeeForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, EmployeeForm
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from decimal import Decimal
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee/employee_list.html', {'employees': employees})

def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employee/employee_detail.html', {'employee': employee})

def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employee_form.html', {'form': form})

def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employee_form.html', {'form': form})

def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'employee_confirm_delete.html', {'employee': employee})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        employee_form = EmployeeForm(request.POST)
        if user_form.is_valid() and employee_form.is_valid():
            user = user_form.save()
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()
            auth_login(request, user)  # Automatically log in after registration
            return redirect('employee_list')
    else:
        user_form = UserRegistrationForm()
        employee_form = EmployeeForm()
    return render(request, 'employee/register.html', {'user_form': user_form, 'employee_form': employee_form})

class LoginView(auth_views.LoginView):
    template_name = 'attendance/login.html'

class LogoutView(auth_views.LogoutView):
    template_name = 'logged_out.html'

# Function to check if the user has the Admin role
def admin_only(user):
    return user.employee.role == 'Admin'

# View to create an employee, only accessible by Admin
@user_passes_test(admin_only)
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employee_form.html', {'form': form})

# Restrict access to only Admin users for employee deletion
@user_passes_test(admin_only)
def employee_delete(request, pk):
    employee = Employee.objects.get(pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'employee_confirm_delete.html', {'employee': employee})

@user_passes_test(admin_only, login_url='/login/')
def employee_create(request):
    # Admin-only employee creation view
    pass

def employee_dashboard(request):
    employee = Employee.objects.get(user=request.user)
    context = {
        'name': employee.name,
        'work_hours': employee.work_hours,
        'expected_salary': employee.expected_salary,
    }
    return render(request, 'employee_dashboard.html', context)

def calculate_overtime(employee):
    # Constants
    STANDARD_HOURS = Decimal(40)  # Standard work hours in a week
    OVERTIME_RATE = Decimal(1.5)    # Overtime pay rate

    total_hours = employee.work_hours
    hourly_rate = employee.hourly_rate

    if total_hours > STANDARD_HOURS:
        overtime_hours = total_hours - STANDARD_HOURS
        overtime_pay = overtime_hours * hourly_rate * OVERTIME_RATE
    else:
        overtime_pay = Decimal(0)

    return overtime_pay

