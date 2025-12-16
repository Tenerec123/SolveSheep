from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('MainApp.urls')),
    path('disp/', include('ProblemDisplayer.urls')),
    path('interface/', include('ProblemInterface.urls')),
    path('search', include('Searching.urls')),
    path('authentication/', include('UsersApp.urls')),
    path('training/', include('Training.urls')),
    path('account/', include("AccountInterface.urls")),
    path("django-check-seo/", include("django_check_seo.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)