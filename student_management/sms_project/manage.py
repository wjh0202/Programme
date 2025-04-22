#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
"""
Django 的命令行工具，用于执行管理任务。
例如：运行开发服务器、进行数据库迁移等。
"""
import os
import sys


def main():
    """Run administrative tasks."""
    """
    执行 Django 管理任务的主函数。

    该函数的主要功能包括：
    1. 设置环境变量 DJANGO_SETTINGS_MODULE，指定项目的配置文件。
    2. 尝试导入 Django 的 execute_from_command_line 函数，如果导入失败，则抛出 ImportError 并提示可能的原因。
    3. 根据命令行参数执行相应的 Django 命令。
    """
    # 设置默认的 Django 配置模块
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sms_project.settings")
    try:
        # 导入 Django 的命令行执行工具
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # 如果导入失败，抛出自定义错误信息
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # 根据命令行参数执行 Django 命令
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    # 如果脚本直接运行，则调用 main 函数
    main()

