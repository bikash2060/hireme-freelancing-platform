from django.urls import path, include

urlpatterns = [
    path("", include("home.urls")),
    path("home/", include("home.urls", namespace="homes")),
    path("account/", include("accounts.urls", namespace="accounts")),  
    path("dashboard/", include("clientdashboard.urls", namespace="clientdashboard")),
    path("profiles/", include("profiles.urls")),
]
