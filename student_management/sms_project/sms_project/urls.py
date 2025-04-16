"""
URL configuration for sms_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
# sms_project/sms_project/urls.py
from sms_app import views


app_name = 'sms_app'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/add/', views.StudentCreateView.as_view(), name='add_student'),
    path('students/<str:pk>/edit/', views.StudentUpdateView.as_view(), name='edit_student'),
    path('students/<str:pk>/delete/', views.StudentDeleteView.as_view(), name='delete_student'),
    path('scores/', views.ScoreListView.as_view(), name='score_list'),
    path('scores/add/', views.ScoreCreateView.as_view(), name='add_score'),
    path('scores/<int:pk>/edit/', views.ScoreUpdateView.as_view(), name='edit_score'),
    path('scores/<int:pk>/update/', views.ScoreUpdateView.as_view(), name='update_score'),
    path('scores/<int:pk>/delete/', views.ScoreDeleteView.as_view(), name='delete_score'),
    path('api/scores/<str:student_id>/', views.get_student_scores, name='get_student_scores'),
    path('', views.DashboardView.as_view(), name='dashboard'),
]

