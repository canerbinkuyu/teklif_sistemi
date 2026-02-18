from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # accounts uygulaması (login, signup, password vs.)
    path("accounts/", include("accounts.urls")),
    # products uygulaması
    path("products/", include("products.urls")),

]

# Development için media files serve et
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
