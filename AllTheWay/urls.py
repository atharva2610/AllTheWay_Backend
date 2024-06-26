from django.contrib import admin
from django.urls import path, include
from Customer import views
from django.contrib.auth import views as auth_views


urlpatterns = [
     path('admin/', admin.site.urls),
     path('', views.home, name='home'),
     path('password-reset/', views.ResetPasswordView.as_view(), name='password_reset'),
     path('password-reset-confirm/<uidb64>/<token>/',
          auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
          name='password_reset_confirm'),
     path('password-reset-complete/',
          auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
          name='password_reset_complete'),
     path('api/', include('Customer.urls')),
     path('api/owner/', include('Owner.urls')),
     path('api/address/', include('Address.urls')),
     path('api/account/', include('Account.urls')),
]