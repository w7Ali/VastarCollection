from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("z-apparel/", admin.site.urls),
    path("", include("app.urls")),
]
