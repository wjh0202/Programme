from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class ClassInformation(models.Model):
    ClassID = models.CharField(max_length=20, primary_key=True, verbose_name=_('班级编号'))
    ClassName = models.CharField(max_length=100, verbose_name=_('班级名称'))
    Grade = models.CharField(max_length=50, verbose_name=_('年级'))
    ClassAdviser = models.CharField(max_length=100, verbose_name=_('班主任'))
    CreatedAt = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    UpdatedAt = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))

    class Meta:
        verbose_name = _('班级信息')
        verbose_name_plural = _('班级信息')
        ordering = ['-CreatedAt']

    def __str__(self):
        return self.ClassName

class Student(models.Model):
    StudentID = models.CharField(max_length=20, primary_key=True, verbose_name=_('学号'))
    Name = models.CharField(max_length=100, verbose_name=_('姓名'))
    Gender = models.CharField(max_length=10, choices=[('男', '男'), ('女', '女')], verbose_name=_('性别'))
    Age = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(150)],
        verbose_name=_('年龄')
    )
    Class = models.ForeignKey(ClassInformation, on_delete=models.CASCADE, verbose_name=_('班级'))
    EnrollmentDate = models.DateField(verbose_name=_('入学日期'))
    Phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('联系电话'))
    Email = models.EmailField(blank=True, null=True, verbose_name=_('电子邮箱'))
    Address = models.TextField(blank=True, null=True, verbose_name=_('家庭住址'))
    CreatedAt = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    UpdatedAt = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))

    class Meta:
        verbose_name = _('学生信息')
        verbose_name_plural = _('学生信息')
        ordering = ['-CreatedAt']

    def __str__(self):
        return f"{self.Name} ({self.StudentID})"

class Course(models.Model):
    CourseID = models.CharField(max_length=20, primary_key=True, verbose_name=_('课程编号'))
    CourseName = models.CharField(max_length=100, verbose_name=_('课程名称'))
    CourseDescription = models.TextField(verbose_name=_('课程描述'))
    Credits = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_('学分')
    )
    CreatedAt = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    UpdatedAt = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))

    class Meta:
        verbose_name = _('课程信息')
        verbose_name_plural = _('课程信息')
        ordering = ['CourseName']

    def __str__(self):
        return self.CourseName

class Score(models.Model):
    ScoreID = models.AutoField(primary_key=True, verbose_name=_('成绩编号'))
    Student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_('学生'))
    Course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_('课程'))
    RegularGrade = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('平时成绩')
    )
    MidtermGrade = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('期中成绩')
    )
    FinalGrade = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('期末成绩')
    )
    CreatedAt = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    UpdatedAt = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))

    class Meta:
        verbose_name = _('成绩信息')
        verbose_name_plural = _('成绩信息')
        ordering = ['-CreatedAt']
        unique_together = ['Student', 'Course']

    def __str__(self):
        return f"{self.Student.Name} - {self.Course.CourseName}"

    @property
    def total_grade(self):
        """计算总成绩"""
        try:
            return round(self.RegularGrade * 0.3 + self.MidtermGrade * 0.3 + self.FinalGrade * 0.4, 2)
        except (TypeError, AttributeError):
            return 0.0

    @property
    def grade_level(self):
        """获取成绩等级"""
        try:
            total = self.total_grade
            if total >= 90:
                return 'A'
            elif total >= 80:
                return 'B'
            elif total >= 70:
                return 'C'
            elif total >= 60:
                return 'D'
            else:
                return 'F'
        except (TypeError, AttributeError):
            return 'F'