from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
]
