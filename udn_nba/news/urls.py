from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"authors", views.AuthorViewSet)
router.register(r"sessions", views.NewsSessionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
