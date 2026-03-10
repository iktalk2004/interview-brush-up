from django.urls import path
from .views import AdminAlgorithmCompareView, AdminTriggerSimilarityView

urlpatterns = [
    path('recommend/compare', AdminAlgorithmCompareView.as_view(), name='admin_recommend_compare'),
    path('recommend/trigger', AdminTriggerSimilarityView.as_view(), name='admin_trigger_similarity'),
]