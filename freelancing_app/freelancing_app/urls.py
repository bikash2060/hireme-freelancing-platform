from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("home.urls", namespace="homes")),
    path("account/", include("accounts.urls", namespace="accounts")),  
    path("dashboard/", include("clientdashboard.urls", namespace="clientdashboard")),
]

handler404 = 'home.views.handling_404'

if settings.DEBUG:  
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)