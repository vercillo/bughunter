from django.contrib import admin
from django.urls import path
from bugs.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', bug_list, name='bug_list'),
    path('bugs/new/', bug_create, name='bug_create'),
    path('bugs/<int:bug_id>/detail', bug_detail, name='bug_detail'),
    path('bugs/<int:bug_id>/edit/', bug_edit, name='bug_edit'),
]
