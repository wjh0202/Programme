# 学生成绩管理系统

一个基于Django框架开发的学生成绩管理系统，提供学生信息管理、成绩录入、查询和统计等功能。

## 功能特点

- 学生信息管理
  - 添加、编辑、删除学生信息
  - 学生基本信息维护（学号、姓名、性别、年龄等）
  - 班级分配管理

- 成绩管理
  - 成绩录入（平时成绩、期中成绩、期末成绩）
  - 成绩查询和统计
  - 自动计算总成绩和等级评定
  - 成绩修改和删除

- 班级管理
  - 班级信息维护
  - 班级学生分布统计

- 课程管理
  - 课程信息维护
  - 课程学分设置

- 用户功能
  - 用户登录/注销
  - 个人信息查看
  - 系统使用统计

## 技术栈

- 后端框架：Django 4.2.7
- 前端框架：Bootstrap 5
- 数据库：SQLite（开发环境）
- 开发语言：Python 3.8

## 项目结构

```
sms_project/
├── sms_app/                # 主应用
│   ├── migrations/         # 数据库迁移文件
│   ├── templates/          # 模板文件
│   │   ├── base.html      # 基础模板
│   │   ├── dashboard.html # 仪表盘
│   │   ├── students/      # 学生相关模板
│   │   └── scores/        # 成绩相关模板
│   ├── models.py          # 数据模型
│   ├── views.py           # 视图函数
│   ├── urls.py            # URL配置
│   └── forms.py           # 表单类
├── sms_project/           # 项目配置
│   ├── settings.py        # 项目设置
│   ├── urls.py            # 主URL配置
│   └── wsgi.py           # WSGI配置
├── static/                # 静态文件
├── logs/                  # 日志文件
└── manage.py             # Django管理脚本
```

## 数据模型

- `Student`: 学生信息
- `ClassInformation`: 班级信息
- `Course`: 课程信息
- `Score`: 成绩信息

## 安装和运行

1. 克隆项目
```bash
git clone [项目地址]
cd sms_project
```

2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 数据库迁移
```bash
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

7. 访问系统
打开浏览器访问 http://127.0.0.1:8000

## 使用说明

1. 登录系统
   - 使用超级用户账号登录系统
   - 或使用具有相应权限的普通用户账号

2. 学生管理
   - 在导航栏点击"学生管理"
   - 可以查看、添加、编辑和删除学生信息

3. 成绩管理
   - 在导航栏点击"成绩管理"
   - 可以录入、查询和修改学生成绩
   - 系统自动计算总成绩和等级

4. 查看统计信息
   - 在仪表盘页面查看系统统计信息
   - 包括学生总数、班级分布、平均成绩等

## 开发计划

- [ ] 添加成绩导入/导出功能
- [ ] 实现成绩分析图表
- [ ] 添加学生成绩单生成功能
- [ ] 优化用户权限管理
- [ ] 添加数据备份功能

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 联系方式

如有任何问题或建议，请联系项目维护者。