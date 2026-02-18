from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # accounts (login, signup, password, redirect vs.)
    path("accounts/", include("accounts.urls")),

    # products
    path("products/", include("products.urls")),
]
