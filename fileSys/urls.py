"""
URL configuration for fileSys project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import TemplateView

from fileApp import views as fileview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__reload__/', include('django_browser_reload.urls')),
    path('password_reset/', fileview.password_reset_request, name='password_reset'),
    path('reset/<uidb64>/<token>/', fileview.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset/done/', TemplateView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/done/', TemplateView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('signup/', fileview.SignupView.as_view(), name='signup'),
    path('login/', fileview.LoginView.as_view(), name='login'),
    path('files/', fileview.FileFeed.as_view(), name="files"),
    path('share_file/', fileview.share_file, name='share_file'),
    path('download_file/', fileview.download_file, name='download_file'),
]

urlpatterns += static (settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)