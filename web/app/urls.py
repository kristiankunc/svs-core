from django.urls import path

from .views import base, services, templates

urlpatterns = []

urlpatterns += base.urlpatterns
urlpatterns += services.urlpatterns
urlpatterns += templates.urlpatterns
