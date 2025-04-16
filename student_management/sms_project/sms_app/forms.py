from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, ButtonHolder, HTML
from .models import Student, Score, Course
from django.urls import reverse_lazy

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['StudentID', 'Name', 'Gender', 'Age', 'Class', 'EnrollmentDate', 'Phone', 'Email', 'Address']
        labels = {
            'StudentID': _('学号'),
            'Name': _('姓名'),
            'Gender': _('性别'),
            'Age': _('年龄'),
            'Class': _('班级'),
            'EnrollmentDate': _('入学日期'),
            'Phone': _('联系电话'),
            'Email': _('电子邮箱'),
            'Address': _('家庭住址')
        }
        widgets = {
            'EnrollmentDate': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'Gender': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'Class': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'Phone': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': _('请输入联系电话')}
            ),
            'Email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': _('请输入电子邮箱')}
            ),
            'Address': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('请输入家庭住址')}
            )
        }
        error_messages = {
            'StudentID': {
                'unique': _('该学号已存在'),
                'required': _('请输入学号')
            },
            'Name': {
                'required': _('请输入姓名')
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Fieldset(
                _('基本信息'),
                Row(
                    Column('StudentID', css_class='form-group col-md-6'),
                    Column('Name', css_class='form-group col-md-6'),
                    css_class='form-row'
                ),
                Row(
                    Column('Gender', css_class='form-group col-md-4'),
                    Column('Age', css_class='form-group col-md-4'),
                    Column('Class', css_class='form-group col-md-4'),
                    css_class='form-row'
                ),
                'EnrollmentDate',
            ),
            Fieldset(
                _('联系方式'),
                Row(
                    Column('Phone', css_class='form-group col-md-6'),
                    Column('Email', css_class='form-group col-md-6'),
                    css_class='form-row'
                ),
                'Address',
            ),
            ButtonHolder(
                Submit('submit', _('保存'), css_class='btn btn-primary'),
                css_class='d-flex justify-content-end mt-3'
            )
        )

    def clean_StudentID(self):
        student_id = self.cleaned_data.get('StudentID')
        if not student_id.isdigit():
            raise ValidationError(_('学号必须为数字'))
        return student_id

    def clean_Age(self):
        age = self.cleaned_data.get('Age')
        if age < 0 or age > 150:
            raise ValidationError(_('年龄必须在0-150岁之间'))
        return age

    def clean_Phone(self):
        phone = self.cleaned_data.get('Phone')
        if phone and not phone.isdigit():
            raise ValidationError(_('联系电话必须为数字'))
        return phone

    def clean_Email(self):
        email = self.cleaned_data.get('Email')
        if email and '@' not in email:
            raise ValidationError(_('请输入有效的电子邮箱地址'))
        return email

from .models import Score

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = ['Student', 'Course', 'RegularGrade', 'MidtermGrade', 'FinalGrade']
        labels = {
            'Student': _('学生'),
            'Course': _('课程'),
            'RegularGrade': _('平时成绩'),
            'MidtermGrade': _('期中成绩'),
            'FinalGrade': _('期末成绩')
        }
        widgets = {
            'Student': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'Course': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'RegularGrade': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '100'}
            ),
            'MidtermGrade': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '100'}
            ),
            'FinalGrade': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '100'}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Fieldset(
                _('成绩信息'),
                Row(
                    Column('Student', css_class='form-group col-md-6'),
                    Column('Course', css_class='form-group col-md-6'),
                    css_class='form-row'
                ),
                Row(
                    Column('RegularGrade', css_class='form-group col-md-4'),
                    Column('MidtermGrade', css_class='form-group col-md-4'),
                    Column('FinalGrade', css_class='form-group col-md-4'),
                    css_class='form-row'
                ),
            ),
            ButtonHolder(
                Submit('submit', _('保存'), css_class='btn btn-primary'),
                HTML('<a href="{}" class="btn btn-secondary">{}</a>'.format(
                    reverse_lazy('score_list'),
                    _('取消')
                )),
                css_class='d-flex justify-content-end mt-3'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('Student')
        course = cleaned_data.get('Course')
        
        # 检查是否已存在该学生的该课程成绩
        if self.instance.pk is None:  # 新增成绩时检查
            if Score.objects.filter(Student=student, Course=course).exists():
                raise ValidationError(_('该学生已有该课程的成绩记录'))

        # 验证成绩范围
        for field in ['RegularGrade', 'MidtermGrade', 'FinalGrade']:
            grade = cleaned_data.get(field)
            if grade is not None and (grade < 0 or grade > 100):
                self.add_error(field, _('成绩必须在0-100分之间'))

        return cleaned_data