# 学生成绩管理系统

一个基于Django开发的学生成绩管理系统，提供学生信息管理、成绩管理、数据导入导出等功能。

## 功能特性

### 1. 用户管理
- 用户登录/登出
- 权限控制
- 用户个人资料

### 2. 学生管理
- 学生信息的增删改查
- 学生列表分页显示
- 学生信息搜索功能

### 3. 班级管理
- 班级信息的增删改查
- 班级学生统计

### 4. 课程管理
- 课程信息的增删改查
- 课程学分管理

### 5. 成绩管理
- 成绩录入和修改
- 成绩统计和分析
- 成绩等级评定
- Excel批量导入导出
- 成绩模板下载

### 6. 数据统计
- 学生总数统计
- 班级分布统计
- 成绩分布统计
- 最近活动记录

## 技术栈

- Python 3.8+
- Django 4.2+
- Bootstrap 5
- jQuery
- pandas
- openpyxl

## 安装步骤

1. 克隆项目
```bash
git clone [项目地址]
cd student_management
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置数据库
```bash
python manage.py makemigrations
python manage.py migrate
```

5. 创建超级用户
```bash
python manage.py createsuperuser
```

6. 运行开发服务器
```bash
python manage.py runserver
```

## 使用说明

### 1. 登录系统
- 访问 http://localhost:8000/login/
- 使用超级用户账号登录

### 2. 学生管理
- 添加学生：填写学生基本信息
- 修改学生：更新学生信息
- 删除学生：删除学生记录
- 搜索学生：支持按姓名、学号、班级搜索

### 3. 成绩管理
- 手动录入：单个学生成绩录入
- 批量导入：使用Excel模板批量导入
- 成绩导出：导出所有成绩到Excel
- 成绩统计：查看成绩分布和统计

### 4. 数据导入导出
- 下载模板：获取标准Excel导入模板
- 导入数据：上传填写好的Excel文件
- 导出数据：导出当前数据到Excel

## 项目结构

```
sms_project/
├── manage.py
├── requirements.txt
├── sms_app/
│   ├── models.py      # 数据模型
│   ├── views.py       # 视图函数
│   ├── urls.py        # URL配置
│   ├── forms.py       # 表单类
│   └── templates/     # 模板文件
├── static/            # 静态文件
└── logs/             # 日志文件
```

## 注意事项

1. 成绩导入
   - 使用标准Excel模板
   - 确保学号和课程编号存在
   - 成绩范围：0-100

2. 数据安全
   - 定期备份数据库
   - 及时更新系统
   - 保护用户密码

3. 性能优化
   - 使用缓存减少数据库查询
   - 分页显示大量数据
   - 异步处理耗时操作

## 常见问题

1. 导入成绩失败
   - 检查Excel文件格式
   - 确认学号和课程编号存在
   - 验证成绩数据格式

2. 登录问题
   - 确认用户名密码正确
   - 检查用户权限设置
   - 清除浏览器缓存

## 许可证

本项目采用 MIT 许可证 