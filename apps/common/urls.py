from django.urls import path

from apps.common.views import health_check_celery, health_check_redis
from apps.common.api_endpoints.common.UsefulLinkList.views import UsefulLinkListAPIView
from apps.common.api_endpoints.common.UsefulLinkDetail.views import UsefulLinkDetailAPIView
from apps.common.api_endpoints.common.RegionList.views import RegionListAPIView
from apps.common.api_endpoints.common.DistrictList.views import DistrictListAPIView

from .api_endpoints import FrontendTranslationView, VersionHistoryView

app_name = "common"

urlpatterns = [
    path(
        "FrontendTranslations/",
        FrontendTranslationView.as_view(),
        name="frontend-translations",
    ),
    path("VersionHistory/", VersionHistoryView.as_view(), name="version-history"),
    path("useful-link/list/", UsefulLinkListAPIView.as_view(), name="useful-link-list"),
    path("useful-link/detail/<slug:slug>/", UsefulLinkDetailAPIView.as_view(), name="useful-link-detail"),
    path("regions/", RegionListAPIView.as_view(), name="region-list"),
    path("districts/", DistrictListAPIView.as_view(), name="district-list"),
    path("health-check/redis/", health_check_redis, name="health-check-redis"),
    path("health-check/celery/", health_check_celery, name="health-check-celery"),
]
