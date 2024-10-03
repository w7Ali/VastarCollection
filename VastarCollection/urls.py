from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("mr-hidden/", admin.site.urls),
    path("", include("app.urls")),
]
