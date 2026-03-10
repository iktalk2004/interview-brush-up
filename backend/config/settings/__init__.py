import os 

env = os.getenv('DJANGO_ENV', 'development')

# 环境变量配置, 开发环境使用 development, 生产环境使用 production
if env == 'production':
    from .production import *
else:
    from .development import *
