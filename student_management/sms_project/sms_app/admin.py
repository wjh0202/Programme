from django.contrib import admin
from .models import ClassInformation, Student, Course, Score

admin.site.register(ClassInformation)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Score)