from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import EmployeeRegisterForm, EmployeeLoginForm
from .models import AuthCode, TimeLog
from django.utils import timezone
from employee.models import Employee
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404
from .models import Attendance
from django.contrib.auth.decorators import login_required
from .forms import LeaveRequestForm
from django.contrib.auth.forms import UserCreationForm
from .models import LeaveRequest
from django.http import HttpResponseRedirect
from decimal import Decimal

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after successful registration
    else:
        form = UserCreationForm()

    return render(request, 'attendance/register.html', {'form': form})


def employee_login(request):
    if request.method == 'POST':
        form = EmployeeLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            auth_code = form.cleaned_data.get('auth_code')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                code_obj = AuthCode.objects.filter(user=user, code=auth_code, is_active=True).first()
                if code_obj:
                    login(request, user)
                    return redirect('time_in')
                else:
                    form.add_error('auth_code', 'Invalid authentication code')
    else:
        form = EmployeeLoginForm()
    return render(request, 'attendance/login.html', {'form': form})


@login_required
def time_in(request):
    if request.method == "POST":
        # Create a new TimeLog entry for the user
        TimeLog.objects.create(user=request.user, time_in=timezone.now())
        return redirect('time_log')  # Redirect to the time log page

    return render(request, 'attendance/time_in.html')


@login_required
def time_out(request):
    if request.method == "POST":
        # Get the latest time log entry for the user
        time_log = TimeLog.objects.filter(user=request.user, time_out=None).last()
        if time_log:
            time_log.time_out = timezone.now()
            time_log.save()
        return redirect('time_log')  # Redirect to the time log page

    return render(request, 'attendance/time_out.html')


@login_required
def time_log(request):
    user = request.user
    try:
        employee = Employee.objects.get(user=user)
        total_hours_today = TimeLog.total_hours_today(user)
        total_hours_this_month = TimeLog.total_hours_this_month(user)
        daily_salary = employee.calculate_daily_salary()
        monthly_salary = employee.calculate_monthly_salary()

        context = {
            'employee': employee,
            'total_hours_today': total_hours_today,
            'total_hours_this_month': total_hours_this_month,
            'daily_salary': daily_salary,
            'monthly_salary': monthly_salary,
        }

        return render(request, 'attendance/time_log.html', context)

    except Employee.DoesNotExist:
        return render(request, 'attendance/time_log.html', {'error': "Employee record not found."})

    except Exception as e:
        print(f"An error occurred in time_log: {e}")
        return render(request, 'attendance/time_log.html', {'error': "An error occurred while processing your request."})

@login_required
def logout_view(request):
    logout(request)  # Log out the user
    return redirect('login')  # Redirect to the login page or wherever you want


@login_required
def employee_info(request):
    user = request.user
    try:
        employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        # Handle the case where the employee record does not exist
        return render(request, 'attendance/employee_info.html', {'error': 'Employee profile not found.'})

    context = {
        'employee': employee,
    }

    return render(request, 'attendance/employee_info.html', context)

def attendance_redirect_view(request, attendance_id):
    attendance = Attendance.objects.get(pk=attendance_id)
    return redirect(attendance.get_absolute_url())

def employee_info_view(request, employee_id):
    employee = Employee.objects.get(pk=employee_id)
    attendance = Attendance.objects.filter(employee=employee).last()  # Latest attendance record
    return render(request, 'employee_info.html', {'employee': employee, 'attendance': attendance})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Logs in the employee
            employee = user  # Assuming 'user' is the employee

            # Fetch the latest attendance record for this employee
            try:
                attendance = Attendance.objects.filter(employee=employee).last()
                # Redirect to the absolute URL based on attendance status
                return redirect(attendance.get_absolute_url())
            except Attendance.DoesNotExist:
                # If no attendance record exists, redirect to a default page (e.g., time in page)
                return redirect('attendance_log_time_in', pk=employee.pk)

        else:
            # Invalid login, handle error (e.g., render the login form again)
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    # Render login form if GET request
    return render(request, 'login.html')
def register_view(request):
    # Registration logic
    if form.is_valid():
        new_employee = form.save()
        return redirect('employee_info', employee_id=new_employee.pk)

def attendance_detail_view(request, pk):
    # Get the specific attendance record
    attendance = get_object_or_404(Attendance, pk=pk)
    return render(request, 'attendance/attendance_detail.html', {'attendance': attendance})

def attendance_summary_view(request, pk):
    # Get the specific attendance record and show a summary
    attendance = get_object_or_404(Attendance, pk=pk)
    return render(request, 'attendance/attendance_summary.html', {'attendance': attendance})

def attendance_log_time_in_view(request, pk):
    # Add your logic here for logging time in
    context = {}
    return render(request, 'attendance/log_time_in.html', context)


@login_required
def request_leave(request):
    if request.method == "POST":
        leave_type = request.POST['leave_type']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        reason = request.POST.get('reason', 'No reason provided')

        LeaveRequest.objects.create(
            employee=request.user,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='Pending'
        )

        return redirect('leave_status')  # Redirect to leave status after submission
    return render(request, 'attendance/request_leave.html')

@login_required
def leave_status(request):
    leave_requests = LeaveRequest.objects.filter(employee=request.user)
    return render(request, 'attendance/leave_status.html', {'leave_requests': leave_requests})

@login_required
def payroll_info(request):
    employee = Employee.objects.get(user=request.user)

    # Assume work_hours is a Decimal field
    hours_worked = Decimal(employee.work_hours)  # Convert to Decimal if needed

    # Calculate daily and monthly salary
    daily_salary = employee.salary * hours_worked  # Both are Decimal now
    monthly_salary = employee.salary * Decimal(160)  # Assuming a standard work month

    context = {
        'employee': employee,
        'daily_salary': daily_salary,
        'monthly_salary': monthly_salary,
    }

    return render(request, 'attendance/payroll_info.html', context)

