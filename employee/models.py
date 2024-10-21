from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from attendance.models import TimeLog
from django import forms


class Employee(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Staff', 'Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    position = models.CharField(max_length=100, default='Staff')  # Set a default value here
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)  # Set a default value here
    work_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Work hours in decimal form

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


    def get_absolute_url(self):
        if self.time_out:
            # If time out is logged, redirect to the summary or time log page
            return reverse('attendance_summary', kwargs={'pk': self.pk})
        elif self.time_in:
            # If time in is logged but not time out, redirect to attendance details
            return reverse('attendance_detail', kwargs={'pk': self.pk})
        else:
            # If no time in or out, maybe redirect to log time in page
            return reverse('attendance_log_time_in', kwargs={'pk': self.employee.pk})


    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def calculate_daily_salary(self):
        try:
            total_hours = TimeLog.total_hours_today(self.user)  # Pass user, not self
            if total_hours is None:
                total_hours = 0
            return total_hours * self.hourly_rate
        except Exception as e:
            print(f"Error calculating daily salary: {e}")
            return 0  # Default to 0 if there's an error

    def calculate_monthly_salary(self):
        try:
            total_hours = TimeLog.total_hours_this_month(self.user)
            if total_hours is None:
                total_hours = 0
            return total_hours * self.hourly_rate
        except Exception as e:
            print(f"Error calculating monthly salary: {e}")
            return 0  # Default to 0 if there's an error

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class EmployeeForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Employee
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'phone',
            'department',
            'hire_date',
            'salary',
            'status',
            'role',
            'position',
            'hourly_rate',
            'work_hours',
        ]

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
        )
        user.set_password(self.cleaned_data['password'])  # Set the password
        if commit:
            user.save()
        employee = super().save(commit=False)
        employee.user = user
        if commit:
            employee.save()
        return employee