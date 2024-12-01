from django.urls import path, include
from . import views

app_name = 'homes'

urlpatterns = [
    path("", views.home_page, name="home"),
]

