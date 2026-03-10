from django.urls import path
from .views import CollectionListView, CollectionRemoveView, CollectionCheckView

urlpatterns = [
    path('', CollectionListView.as_view(), name='collection_list'),
    path('<int:question_id>', CollectionRemoveView.as_view(), name='collection_remove'),
    path('<int:question_id>/check', CollectionCheckView.as_view(), name='collection_check'),
]