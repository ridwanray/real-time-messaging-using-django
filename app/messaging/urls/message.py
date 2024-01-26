from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..views import MessageViewsets

app_name = "message"

router = DefaultRouter()
router.register("", MessageViewsets)

urlpatterns = [
    path("", include(router.urls)),
]
