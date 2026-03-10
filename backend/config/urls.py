from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # 用户认证
    path('api/v1/auth/', include('apps.users.urls.auth_urls')),
    # 用户个人
    path('api/v1/user/', include('apps.users.urls.user_urls')),
    # 分类
    path('api/v1/categories/', include('apps.questions.urls_categories')),
    # 题目
    path('api/v1/questions/', include('apps.questions.urls')),
    # 刷题
    path('api/v1/practice/', include('apps.practice.urls')),
    # 答题提交
    path('api/v1/submit/', include('apps.practice.urls_submit')),
    # 评论
    path('api/v1/comments/', include('apps.comments.urls')),
    # 收藏
    path('api/v1/collections/', include('apps.collections_app.urls')),
    # 统计
    path('api/v1/stats/', include('apps.stats.urls')),
    # 公告
    path('api/v1/announcements/', include('apps.announcements.urls')),
    # 推荐
    path('api/v1/recommend/', include('apps.recommend.urls')),
    # 评分
    path('api/v1/scoring/', include('apps.scoring.urls')),
    # 评测
    path('api/v1/judge/', include('apps.judge.urls')),



    # 管理员
    path('api/v1/admin/', include('apps.users.urls.admin_urls')),
    path('api/v1/admin/', include('apps.questions.urls_admin')),
    path('api/v1/admin/', include('apps.stats.urls_admin')),
    path('api/v1/admin/', include('apps.announcements.urls_admin')),
    path('api/v1/admin/', include('apps.recommend.urls_admin')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
