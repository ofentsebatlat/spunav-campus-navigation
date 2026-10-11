from django.urls import path
from . import views

app_name = 'navigation'

urlpatterns = [
    path('', views.home, name='home'),
    path('find-route/', views.find_route, name='find_route'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
