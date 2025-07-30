"""
URL configuration for tests.
"""

from django.urls import path, include
from turbodrf.router import TurboDRFRouter
from turbodrf.documentation import get_turbodrf_schema_view

# Create the TurboDRF router
router = TurboDRFRouter()

# Get the schema view
schema_view = get_turbodrf_schema_view()

urlpatterns = [
    path("api/", include(router.urls)),
]

# Only add documentation URLs if enabled
if schema_view:
    urlpatterns += [
        path("swagger/", schema_view.with_ui("swagger", cache_timeout=0)),
        path("redoc/", schema_view.with_ui("redoc", cache_timeout=0)),
    ]
