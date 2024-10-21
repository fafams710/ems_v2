from django.urls import path
from .views import logout_view
from .views import employee_info
from . import views
from .views import payroll_info

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.employee_login, name='login'),
    path('time_in/', views.time_in, name='time_in'),
    path('time_out/', views.time_out, name='time_out'),
    path('time_log/', views.time_log, name='time_log'),
    path('logout/', logout_view, name='logout'),
    path('attendance/<int:pk>/detail/', views.attendance_detail_view, name='attendance_detail'),
    path('attendance/<int:pk>/summary/', views.attendance_summary_view, name='attendance_summary'),
    path('attendance/<int:pk>/log-time-in/', views.attendance_log_time_in_view, name='attendance_log_time_in'),
    path('attendance/<int:pk>/log-time-in/', views.attendance_redirect_view, name='attendance_log_time_in'),
    path('request-leave/', views.request_leave, name='request_leave'),
    path('leave-status/', views.leave_status, name='leave_status'),
    path('employee-info/', views.employee_info, name='employee_info'),
    path('request-leave/', views.request_leave, name='request_leave'),
    path('leave-status/', views.leave_status, name='leave_status'),
    path('logout/', views.logout_view, name='logout'),
    path('payroll-info/', payroll_info, name='payroll_info'),
    path('', views.employee_login, name='login'),

]

