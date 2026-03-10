"""
Django 基础配置 - 所有环境共享
"""
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# 项目根目录: backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 加载 .env 文件
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 第三方库
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'django_celery_beat',

    # 自定义应用
    'apps.users',
    'apps.questions',
    'apps.practice',
    'apps.judge',
    'apps.scoring',
    'apps.recommend',
    'apps.comments',
    'apps.collections_app',
    'apps.ratings',
    'apps.stats',
    'apps.announcements',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 自定义用户模型
AUTH_USER_MODEL = 'users.User'

# 语言和时区设置
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件和媒体文件配置
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 跨域请求配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.StandardPagination',  # 自定义分页类
    'PAGE_SIZE': 20,  # 默认每页返回 20 条数据
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',  # 搜索过滤
        'rest_framework.filters.OrderingFilter',  # 排序过滤
    ],
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',  # 自定义异常处理
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',  # 渲染为 JSON 格式
    ],
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
CORS_ALLOWED_CREDENTIALS = True  # 是否允许跨域请求携带凭证（如 Cookies）

# 简单 JWT 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME', 60))),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME', 1440))),
    'ROTATE_REFRESH_TOKENS': True,  # 刷新令牌时是否旋转刷新令牌
    'BLACKLIST_AFTER_ROTATION': True,  # 刷新令牌后是否将旧令牌加入黑名单
    'AUTH_HEADER_TYPES': ('Bearer',),  # 认证头类型
}

# Celery 配置
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']  # 接受的内容类型
CELERY_TASK_SERIALIZER = 'json'  # 任务序列化器
CELERY_RESULT_SERIALIZER = 'json'  # 结果序列化器
CELERY_TIMEZONE = 'Asia/Shanghai'  # 时区设置
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'  # 数据库调度器

# 邮箱配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.qq.com')  # qq 邮箱 SMTP 服务器
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))  # qq 邮箱 SMTP 端口
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False  # 是否使用 TLS 加密
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER', '')

# Judge0 配置
JUDGE0_API_URL = os.getenv('JUDGE0_API_URL', 'http://localhost:2358')
JUDGE0_API_KEY = os.getenv('JUDGE0_API_KEY', '')

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')

# 业务配置
DAILY_RECOMMEND_COUNT = 5  # 每日推荐题目数量
MISTAKE_SCORE_THRESHOLD = 60.0  # 错误率阈值，超过该值则认为是错误
MAX_AVATAR_SIZE = int(os.getenv('MAX_AVATAR_SIZE', 2097152))  # 最大头像文件大小（字节）
VERIFICATION_CODE_EXPIRE = 300  # 验证码过期时间（秒）
VERIFICATION_CODE_INTERVAL = 60  # 验证码发送间隔（秒）

# DeepSeek AI 配置
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
DEEPSEEK_MODEL = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')