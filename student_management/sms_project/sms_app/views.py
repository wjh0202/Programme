from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import logging
from functools import wraps

from .models import Student, ClassInformation, Score, Course
from .forms import StudentForm, ScoreForm

logger = logging.getLogger(__name__)

def handle_exceptions(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {view_func.__name__}: {str(e)}")
            messages.error(request, "操作失败，请稍后重试")
            return redirect('dashboard')
    return wrapper

@handle_exceptions
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"User {username} logged in successfully")
            return redirect('dashboard')
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            return render(request, 'login.html', {'error': '用户名或密码错误！'})
    return render(request, 'login.html')

@login_required
@handle_exceptions
def user_logout(request):
    logger.info(f"User {request.user.username} logged out")
    logout(request)
    return redirect('login')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 使用缓存获取统计数据
        cache_key = 'dashboard_stats'
        stats = cache.get(cache_key)
        
        if stats is None:
            stats = {
                'total_students': Student.objects.count(),
                'total_classes': ClassInformation.objects.count(),
                'total_courses': Course.objects.count(),
                'recent_students': Student.objects.all().order_by('-CreatedAt')[:5],
                'recent_scores': Score.objects.all().order_by('-CreatedAt')[:5],
                'average_scores': Score.objects.aggregate(
                    avg_regular=Avg('RegularGrade'),
                    avg_midterm=Avg('MidtermGrade'),
                    avg_final=Avg('FinalGrade')
                ),
                'class_distribution': ClassInformation.objects.annotate(
                    student_count=Count('student')
                ).values('ClassName', 'student_count')
            }
            cache.set(cache_key, stats, 300)  # 缓存5分钟
        
        context.update(stats)
        return context

class StudentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Student
    template_name = 'students/list.html'
    context_object_name = 'students'
    paginate_by = 10
    permission_required = 'sms_app.view_student'

    def get_queryset(self):
        queryset = Student.objects.select_related('Class')
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(Name__icontains=search_query) |
                Q(StudentID__icontains=search_query) |
                Q(Class__ClassName__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class StudentCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/form.html'
    success_url = reverse_lazy('student_list')
    success_message = "学生 %(Name)s 添加成功！"
    permission_required = 'sms_app.add_student'

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            logger.info(f"Student {form.instance.Name} added successfully")
            cache.delete('dashboard_stats')  # 清除缓存
            return response
        except Exception as e:
            logger.error(f"Error adding student: {str(e)}")
            messages.error(self.request, "添加学生失败，请重试")
            return super().form_invalid(form)

class StudentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/form.html'
    success_url = reverse_lazy('student_list')
    success_message = "学生 %(Name)s 信息更新成功！"
    permission_required = 'sms_app.change_student'

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            logger.info(f"Student {form.instance.Name} updated successfully")
            cache.delete('dashboard_stats')  # 清除缓存
            return response
        except Exception as e:
            logger.error(f"Error updating student: {str(e)}")
            messages.error(self.request, "更新学生信息失败，请重试")
            return super().form_invalid(form)

class StudentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/confirm_delete.html'
    success_url = reverse_lazy('student_list')
    permission_required = 'sms_app.delete_student'

    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            logger.info(f"Student {self.object.Name} deleted successfully")
            cache.delete('dashboard_stats')  # 清除缓存
            return response
        except Exception as e:
            logger.error(f"Error deleting student: {str(e)}")
            messages.error(request, "删除学生失败，请重试")
            return redirect('student_list')

class ScoreListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Score
    template_name = 'scores/list.html'
    context_object_name = 'scores'
    paginate_by = 10
    permission_required = 'sms_app.view_score'

    def get_queryset(self):
        queryset = Score.objects.select_related('Student', 'Course')
        student_id = self.request.GET.get('student_id')
        course_id = self.request.GET.get('course_id')
        
        if student_id:
            queryset = queryset.filter(Student__StudentID=student_id)
        if course_id:
            queryset = queryset.filter(Course__CourseID=course_id)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.all()
        context['courses'] = Course.objects.all()
        return context

class ScoreCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Score
    form_class = ScoreForm
    template_name = 'scores/form.html'
    success_url = reverse_lazy('score_list')
    success_message = "成绩添加成功！"
    permission_required = 'sms_app.add_score'

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            logger.info(f"Score for {form.instance.Student.Name} added successfully")
            cache.delete('dashboard_stats')  # 清除缓存
            return response
        except Exception as e:
            logger.error(f"Error adding score: {str(e)}")
            messages.error(self.request, "添加成绩失败，请重试")
            return super().form_invalid(form)

class ScoreUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Score
    form_class = ScoreForm
    template_name = 'scores/form.html'
    success_url = reverse_lazy('score_list')
    success_message = "成绩更新成功！"
    permission_required = 'sms_app.change_score'

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            logger.info(f"Score for {form.instance.Student.Name} updated successfully")
            cache.delete('dashboard_stats')  # 清除缓存
            return response
        except Exception as e:
            logger.error(f"Error updating score: {str(e)}")
            messages.error(self.request, "更新成绩失败，请重试")
            return super().form_invalid(form)

class ScoreDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Score
    template_name = 'scores/confirm_delete.html'
    success_url = reverse_lazy('score_list')
    permission_required = 'sms_app.delete_score'

    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            logger.info(f"Score for {self.object.Student.Name} deleted successfully")
            cache.delete('dashboard_stats')  # 清除缓存
            return response
        except Exception as e:
            logger.error(f"Error deleting score: {str(e)}")
            messages.error(request, "删除成绩失败，请重试")
            return redirect('score_list')

@require_http_methods(["GET"])
@login_required
def get_student_scores(request, student_id):
    try:
        scores = Score.objects.filter(Student__StudentID=student_id).select_related('Course')
        data = [{
            'course_name': score.Course.CourseName,
            'regular_grade': score.RegularGrade,
            'midterm_grade': score.MidtermGrade,
            'final_grade': score.FinalGrade,
            'total_grade': score.total_grade(),
            'grade_level': score.get_grade_level()
        } for score in scores]
        return JsonResponse({'scores': data})
    except Exception as e:
        logger.error(f"Error getting student scores: {str(e)}")
        return JsonResponse({'error': '获取成绩失败'}, status=500)

class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 获取用户相关的统计数据
        context.update({
            'user': user,
            'total_students': Student.objects.count(),
            'total_scores': Score.objects.count(),
            'recent_activities': [
                {
                    'type': 'score',
                    'description': f'添加了 {score.Student.Name} 的 {score.Course.CourseName} 成绩',
                    'time': score.CreatedAt
                } for score in Score.objects.order_by('-CreatedAt')[:5]
            ]
        })
        return context