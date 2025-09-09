"""
URL configuration for web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from app.views import index, login, logout, template_detail, templates
from django.urls import path

urlpatterns = [
    path("", index, name="index"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("templates/", templates, name="templates"),
    path("templates/<int:template_id>/", template_detail, name="template_detail"),
]
