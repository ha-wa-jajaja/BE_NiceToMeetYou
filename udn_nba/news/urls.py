from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("authors", views.AuthorViewSet)
router.register("sessions", views.NewsSessionViewSet)
router.register("", views.NewsViewSet)

app_name = "news"

urlpatterns = [
    path("", include(router.urls)),
]
