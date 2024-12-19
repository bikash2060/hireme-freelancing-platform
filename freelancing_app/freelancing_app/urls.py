from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("home.urls", namespace="homes")),
    path('accounts/', include('allauth.urls')),
    path('account/', include('accounts.urls', namespace='account')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
]

handler404 = 'home.views.handling_404'

if settings.DEBUG:  
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)