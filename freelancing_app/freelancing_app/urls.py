from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('accounts/', include('allauth.urls')),
    
    # App-specific routes
    path('', include("home.urls", namespace="home")),
    path('account/', include('accounts.urls', namespace='account')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    
    # Profile routes
    path('client/', include('clientprofile.urls', namespace='client-profile')),
    path('freelancer/', include('freelancerprofile.urls', namespace='freelancer-profile')),
    
    # Project-related routes
    path('project/', include('projects.urls', namespace='project')),
    path('proposal/', include('proposals.urls', namespace='proposals')),
    path('contract/', include('contract.urls', namespace='contract')),
    
    # Communication
    path('chat/', include('chat.urls', namespace='chat')),
    path('notification/', include('notification.urls')),
    
    prefix_default_language=True,
)

handler404 = 'home.views.handling_404'

if settings.DEBUG:  
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)