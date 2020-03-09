from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views

app_name = 'attendance'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register_missing/', views.register_lost_kids, name='register_missing'),
    path('verify/', views.verify, name='verify'),
    path('register_kid/', views.register_kid_biometric, name='register_kid'),
    path('all_missing_kids/', views.view_kids, name='all_kids'),
    path('all_biometric/', views.view_registered_biometric, name='all_biometric'),
    path('make_lost/', views.make_lost, name='make_lost'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
