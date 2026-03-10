"""
生产环境配置
"""
import os
from .base import *

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'interview_brush_up'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

SECURE_BROWSER_XSS_FILTER = True  # 开启浏览器 XSS 过滤
SECURE_CONTENT_TYPE_NOSNIFF = True  # 开启浏览器 MIME 类型嗅探
SESSION_COOKIE_SECURE = True  # 开启会话 cookie 仅通过 HTTPS 传输
CSRF_COOKIE_SECURE = True  # 开启 CSRF cookie 仅通过 HTTPS 传输
