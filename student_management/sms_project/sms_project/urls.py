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
# 导入sms_app应用中的视图模块
from sms_app import views


# 定义应用程序的名称
app_name = 'sms_app'

# 定义URL模式列表
urlpatterns = [
    # 管理员界面URL
    path('admin/', admin.site.urls),
    # 用户登录界面URL
    path('login/', views.user_login, name='login'),
    # 用户登出界面URL
    path('logout/', views.user_logout, name='logout'),
    # 用户个人资料界面URL
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    # 学生列表界面URL
    path('students/', views.StudentListView.as_view(), name='student_list'),
    # 添加学生界面URL
    path('students/add/', views.StudentCreateView.as_view(), name='add_student'),
    # 编辑学生信息界面URL
    path('students/<str:pk>/edit/', views.StudentUpdateView.as_view(), name='edit_student'),
    # 删除学生信息界面URL
    path('students/<str:pk>/delete/', views.StudentDeleteView.as_view(), name='delete_student'),
    # 成绩列表界面URL
    path('scores/', views.ScoreListView.as_view(), name='score_list'),
    # 添加成绩界面URL
    path('scores/add/', views.ScoreCreateView.as_view(), name='add_score'),
    # 编辑成绩界面URL
    path('scores/<int:pk>/edit/', views.ScoreUpdateView.as_view(), name='edit_score'),
    # 更新成绩界面URL
    path('scores/<int:pk>/update/', views.ScoreUpdateView.as_view(), name='update_score'),
    # 删除成绩界面URL
    path('scores/<int:pk>/delete/', views.ScoreDeleteView.as_view(), name='delete_score'),
    # 获取学生成绩的API接口URL
    path('api/scores/<str:student_id>/', views.get_student_scores, name='get_student_scores'),
    # 成绩导出界面URL
    path('scores/export/', views.export_scores, name='export_scores'),
    # 成绩导入界面URL
    path('scores/import/', views.import_scores, name='import_scores'),
    # 成绩模板下载界面URL
    path('scores/template/', views.download_template, name='download_template'),
    # 首页界面URL
    path('', views.DashboardView.as_view(), name='dashboard'),
]

