from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TasklModelViewSet


app_name = "api-v1"
router = DefaultRouter()
router.register("task", TasklModelViewSet, basename="task")
urlpatterns = router.urls