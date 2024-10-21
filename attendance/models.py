from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    date = models.DateField(default=timezone.now)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)
    work_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def get_absolute_url(self):
        if self.time_out:
            # If employee has logged out, redirect to a summary page
            return reverse('attendance_summary', kwargs={'pk': self.pk})
        elif self.time_in:
            # If employee has logged in but not logged out, redirect to their attendance details
            return reverse('attendance_detail', kwargs={'pk': self.pk})
        else:
            # If neither, maybe redirect to a page to log time in
            return reverse('attendance_log_time_in', kwargs={'pk': self.employee.pk})


class AuthCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    is_active = models.BooleanField(default=True)  # Add is_active field
    created_at = models.DateTimeField(auto_now_add=True)  # Add created_at field

    def __str__(self):
        return f'{self.user.username} - {self.code}'

class TimeLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)

    def hours_worked(self):
        if self.time_in and self.time_out:
            return (self.time_out - self.time_in).total_seconds() / 3600
        return 0.0

    @classmethod
    def total_hours_today(cls, user):
        today = timezone.now().date()
        time_logs = cls.objects.filter(user=user, time_in__date=today)
        total_hours = sum(log.hours_worked() for log in time_logs)
        return total_hours

    @classmethod
    def total_hours_this_month(cls, user):
        now = timezone.now()
        first_day_of_month = now.replace(day=1)
        time_logs = cls.objects.filter(user=user, time_in__gte=first_day_of_month)
        total_hours = sum(log.hours_worked() for log in time_logs)
        return total_hours

class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('PTO', 'Paid Time Off'),
        ('SICK', 'Sick Leave'),
        ('VACATION', 'Vacation'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255, default='No reason provided')
    status = models.CharField(max_length=10, default='Pending')

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} ({self.start_date} to {self.end_date})"

class EmployeeProfile(models.Model):
    employee = models.OneToOneField(User, on_delete=models.CASCADE)
    total_leaves = models.IntegerField(default=20)  # total leaves per year
    used_leaves = models.IntegerField(default=0)

    @property
    def remaining_leaves(self):
        return self.total_leaves - self.used_leaves
