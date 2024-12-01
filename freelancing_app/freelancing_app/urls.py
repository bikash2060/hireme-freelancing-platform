from django.urls import path, include

urlpatterns = [
    path("", include("home.urls")),
    path("home/", include("home.urls")),
    path("account/", include("accounts.urls", namespace="accounts")),  
    path("dashboard/", include("dashboard.urls", namespace="dashboard")),
    path("profiles/", include("profiles.urls")),
]
