from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("home.urls", namespace="homes")),
    path('accounts/', include('allauth.urls')),
    path('account/', include('accounts.urls', namespace='account')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('client/', include('clientprofile.urls', namespace='client')),
    path('freelancer/', include('freelancerprofile.urls', namespace='freelancer')),
    path('project/', include('projects.urls', namespace='project')),
    path('freelancers/', include('freelancers.urls', namespace='freelancers')),

]

handler404 = 'home.views.handling_404'

if settings.DEBUG:  
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)