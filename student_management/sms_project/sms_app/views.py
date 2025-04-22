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
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
import logging
from functools import wraps
import pandas as pd
from io import BytesIO
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy

from .models import Student, ClassInformation, Score, Course
from .forms import StudentForm, ScoreForm

logger = logging.getLogger(__name__)

def handle_exceptions(view_func):
    """
    装饰器函数，用于捕获视图函数中的异常并记录日志。

    参数:
        view_func (function): 被装饰的视图函数。

    返回:
        function:

    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            # 记录错误日志并返回错误消息
            logger.error(f"Error in {view_func.__name__}: {str(e)}")
            messages.error(request, "操作失败，请稍后重试")
            return redirect('dashboard')
    return wrapper

@handle_exceptions
def user_login(request):
    """
    处理用户登录请求的视图函数。

    参数:
        request (HttpRequest): HTTP请求对象。

    返回:
        HttpResponse: 渲染的登录页面或重定向到仪表盘。
    """
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
    """
    处理用户登出请求的视图函数。

    参数:
        request (HttpRequest): HTTP请求对象。

    返回:
        HttpResponse: 重定向到登录页面。
    """
    logger.info(f"User {request.user.username} logged out")
    logout(request)
    return redirect('login')

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    显示仪表盘页面的类视图。

    属性:
        template_name (str): 使用的模板名称。
    """
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        """
        获取仪表盘页面的上下文数据。

        返回:
            dict: 包含统计数据和缓存信息的上下文字典。
        """
        context = super().get_context_data(**kwargs)

        # 使用缓存获取统计数据
        cache_key = 'dashboard_stats'
        stats = cache.get(cache_key)

        if stats is None:
            # 如果缓存中没有数据，则从数据库中查询并缓存
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
    """
    显示学生列表的类视图。

    属性:
        model (Model): 使用的学生模型。
        template_name (str): 使用的模板名称。
        context_object_name (str): 上下文中使用的变量名。
        paginate_by (int): 每页显示的学生数量。
        permission_required (str): 所需权限。
    """
    model = Student
    template_name = 'students/list.html'
    context_object_name = 'students'
    paginate_by = 10
    permission_required = 'sms_app.view_student'

    def get_queryset(self):
        """
        获取学生查询集，支持按名称、学号或班级名称搜索。

        返回:
            QuerySet: 过滤后的学生查询集。
        """
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
        """
        获取学生列表页面的上下文数据。

        返回:
            dict: 包含搜索查询和其他上下文信息的字典。
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class StudentCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """
    创建学生的类视图。

    属性:
        model (Model): 使用的学生模型。
        form_class (Form): 使用的表单类。
        template_name (str): 使用的模板名称。
        success_url (str): 成功后的重定向URL。
        success_message (str): 成功消息模板。
        permission_required (str): 所需权限。
    """
    model = Student
    form_class = StudentForm
    template_name = 'students/form.html'
    success_url = reverse_lazy('student_list')
    success_message = "学生 %(Name)s 添加成功！"
    permission_required = 'sms_app.add_student'

    def form_valid(self, form):
        """
        处理表单有效时的逻辑。

        返回:
            HttpResponse: 重定向到成功页面或表单无效页面。
        """
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
    """
    更新学生的类视图。

    属性:
        model (Model): 使用的学生模型。
        form_class (Form): 使用的表单类。
        template_name (str): 使用的模板名称。
        success_url (str): 成功后的重定向URL。
        success_message (str): 成功消息模板。
        permission_required (str): 所需权限。
    """
    model = Student
    form_class = StudentForm
    template_name = 'students/form.html'
    success_url = reverse_lazy('student_list')
    success_message = "学生 %(Name)s 信息更新成功！"
    permission_required = 'sms_app.change_student'

    def form_valid(self, form):
        """
        处理表单有效时的逻辑。

        返回:
            HttpResponse: 重定向到成功页面或表单无效页面。
        """
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
    """
    删除学生的类视图。

    属性:
        model (Model): 使用的学生模型。
        template_name (str): 使用的模板名称。
        success_url (str): 成功后的重定向URL。
        permission_required (str): 所需权限。
    """
    model = Student
    template_name = 'students/confirm_delete.html'
    success_url = reverse_lazy('student_list')
    permission_required = 'sms_app.delete_student'

    def delete(self, request, *args, **kwargs):
        """
        处理删除逻辑。

        返回:
            HttpResponse: 重定向到成功页面或错误页面。
        """
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
    """
    显示成绩列表的类视图。

    属性:
        model (Model): 使用的成绩模型。
        template_name (str): 使用的模板名称。
        context_object_name (str): 上下文中使用的变量名。
        paginate_by (int): 每页显示的成绩数量。
        permission_required (str): 所需权限。
    """
    model = Score
    template_name = 'scores/list.html'
    context_object_name = 'scores'
    paginate_by = 10
    permission_required = 'sms_app.view_score'

    def get_queryset(self):
        """
        获取成绩查询集，支持按学生ID或课程ID过滤。

        返回:
            QuerySet: 过滤后的成绩查询集。
        """
        queryset = Score.objects.select_related('Student', 'Course')
        student_id = self.request.GET.get('student_id')
        course_id = self.request.GET.get('course_id')

        if student_id:
            queryset = queryset.filter(Student__StudentID=student_id)
        if course_id:
            queryset = queryset.filter(Course__CourseID=course_id)

        return queryset

    def get_context_data(self, **kwargs):
        """
        获取成绩列表页面的上下文数据。

        返回:
            dict: 包含学生和课程信息的上下文字典。
        """
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.all()
        context['courses'] = Course.objects.all()
        return context

class ScoreCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """
    创建成绩的类视图。

    属性:
        model (Model): 使用的成绩模型。
        form_class (Form): 使用的表单类。
        template_name (str): 使用的模板名称。
        success_url (str): 成功后的重定向URL。
        success_message (str): 成功消息模板。
        permission_required (str): 所需权限。
    """
    model = Score
    form_class = ScoreForm
    template_name = 'scores/form.html'
    success_url = reverse_lazy('score_list')
    success_message = "成绩添加成功！"
    permission_required = 'sms_app.add_score'

    def form_valid(self, form):
        """
        处理表单有效时的逻辑。

        返回:
            HttpResponse: 重定向到成功页面或表单无效页面。
        """
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
    """
    更新成绩的类视图。

    属性:
        model (Model): 使用的成绩模型。
        form_class (Form): 使用的表单类。
        template_name (str): 使用的模板名称。
        success_url (str): 成功后的重定向URL。
        success_message (str): 成功消息模板。
        permission_required (str): 所需权限。
    """
    model = Score
    form_class = ScoreForm
    template_name = 'scores/form.html'
    success_url = reverse_lazy('score_list')
    success_message = "成绩更新成功！"
    permission_required = 'sms_app.change_score'

    def form_valid(self, form):
        """
        处理表单有效时的逻辑。

        返回:
            HttpResponse: 重定向到成功页面或表单无效页面。
        """
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
    """
    删除成绩的类视图。

    属性:
        model (Model): 使用的成绩模型。
        template_name (str): 使用的模板名称。
        success_url (str): 成功后的重定向URL。
        permission_required (str): 所需权限。
    """
    model = Score
    template_name = 'scores/confirm_delete.html'
    success_url = reverse_lazy('score_list')
    permission_required = 'sms_app.delete_score'

    def delete(self, request, *args, **kwargs):
        """
        处理删除逻辑。

        返回:
            HttpResponse: 重定向到成功页面或错误页面。
        """
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
    """
    获取指定学生的成绩数据并返回JSON响应。

    参数:
        request (HttpRequest): HTTP请求对象。
        student_id (str): 学生的唯一标识符。

    返回:
        JsonResponse: 包含成绩数据的JSON响应。
    """
    try:
        scores = Score.objects.filter(Student__StudentID=student_id).select_related('Course')
        data = [{
            'course_name': score.Course.CourseName,
            'regular_grade': score.RegularGrade,
            'midterm_grade': score.MidtermGrade,
            'final_grade': score.FinalGrade,
            'total_grade': score.total_grade,
            'grade_level': score.grade_level
        } for score in scores]
        return JsonResponse({'scores': data})
    except Exception as e:
        logger.error(f"Error getting student scores: {str(e)}")
        return JsonResponse({'error': '获取成绩失败'}, status=500)

class UserProfileView(LoginRequiredMixin, TemplateView):
    """
    显示用户个人资料页面的类视图。

    属性:
        template_name (str): 使用的模板名称。
    """
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        """
        获取用户个人资料页面的上下文数据。

        返回:
            dict: 包含用户信息和相关统计数据的上下文字典。
        """
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

def export_scores(request):
    """导出成绩数据到Excel"""
    try:
        # 获取所有成绩数据
        scores = Score.objects.select_related('Student', 'Course').all()
        
        # 创建DataFrame
        data = []
        for score in scores:
            data.append({
                '学号': score.Student.StudentID,
                '姓名': score.Student.Name,
                '课程编号': score.Course.CourseID,
                '课程名称': score.Course.CourseName,
                '平时成绩': score.RegularGrade,
                '期中成绩': score.MidtermGrade,
                '期末成绩': score.FinalGrade,
                '总成绩': score.total_grade,
                '等级': score.grade_level
            })
        
        df = pd.DataFrame(data)
        
        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='成绩表')
        
        # 设置响应头
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=scores.xlsx'
        
        return response
    except Exception as e:
        logger.error(f"Error exporting scores: {str(e)}")
        messages.error(request, _('导出成绩失败，请稍后重试'))
        return redirect('score_list')

def download_template(request):
    """下载成绩导入模板"""
    try:
        # 创建模板DataFrame
        template_data = {
            '学号': [],
            '课程编号': [],
            '平时成绩': [],
            '期中成绩': [],
            '期末成绩': []
        }
        df = pd.DataFrame(template_data)
        
        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='成绩导入模板')
        
        # 设置响应头
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=score_template.xlsx'
        
        return response
    except Exception as e:
        logger.error(f"Error downloading template: {str(e)}")
        messages.error(request, _('下载模板失败，请稍后重试'))
        return redirect('score_list')

@login_required
@permission_required('sms_app.add_score')
def import_scores(request):
    """导入成绩数据"""
    if request.method == 'POST':
        try:
            # 获取上传的文件
            excel_file = request.FILES['score_file']
            
            # 读取Excel文件，确保课程编号列以字符串形式读取
            df = pd.read_excel(excel_file, dtype={'课程编号': str})
            
            # 验证必要的列是否存在
            required_columns = ['学号', '课程编号', '平时成绩', '期中成绩', '期末成绩']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                messages.error(request, f'Excel文件缺少以下列：{", ".join(missing_columns)}')
                return redirect('score_list')
            
            # 导入数据
            success_count = 0
            error_count = 0
            error_details = []
            
            for index, row in df.iterrows():
                try:
                    # 验证数据
                    student_id = str(row['学号']).strip()
                    course_id = str(row['课程编号']).strip()
                    
                    # 检查学号是否存在
                    if not Student.objects.filter(StudentID=student_id).exists():
                        raise ValueError(f'学号 {student_id} 不存在')
                    
                    # 检查课程编号是否存在
                    if not Course.objects.filter(CourseID=course_id).exists():
                        # 尝试补零后再检查
                        course_id = course_id.zfill(2)  # 补零到2位
                        if not Course.objects.filter(CourseID=course_id).exists():
                            raise ValueError(f'课程编号 {row["课程编号"]} 不存在')
                    
                    # 验证成绩数据
                    try:
                        regular_grade = float(row['平时成绩'])
                        midterm_grade = float(row['期中成绩'])
                        final_grade = float(row['期末成绩'])
                    except ValueError:
                        raise ValueError('成绩必须是数字')
                    
                    # 验证成绩范围
                    if not all(0 <= grade <= 100 for grade in [regular_grade, midterm_grade, final_grade]):
                        raise ValueError('成绩必须在0-100之间')
                    
                    student = Student.objects.get(StudentID=student_id)
                    course = Course.objects.get(CourseID=course_id)
                    
                    # 创建或更新成绩记录
                    score, created = Score.objects.update_or_create(
                        Student=student,
                        Course=course,
                        defaults={
                            'RegularGrade': regular_grade,
                            'MidtermGrade': midterm_grade,
                            'FinalGrade': final_grade
                        }
                    )
                    success_count += 1
                except ValueError as e:
                    error_details.append(f'第{index + 2}行: {str(e)}')
                    error_count += 1
                except Exception as e:
                    error_details.append(f'第{index + 2}行: 未知错误 - {str(e)}')
                    error_count += 1
            
            # 显示导入结果
            if success_count > 0:
                messages.success(request, f"成功导入 {success_count} 条成绩记录")
            if error_count > 0:
                error_message = f"有 {error_count} 条记录导入失败：\n" + "\n".join(error_details)
                messages.warning(request, error_message)
            
            return redirect('score_list')
        except Exception as e:
            logger.error(f"Error importing scores: {str(e)}")
            messages.error(request, f'导入成绩失败：{str(e)}')
            return redirect('score_list')
    return redirect('score_list')
