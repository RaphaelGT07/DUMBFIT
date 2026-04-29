from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "DumbFit Admin"
admin.site.site_title = "DumbFit Admin"
admin.site.index_title = "Gerenciamento da plataforma"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("cadastro.urls")),
]
