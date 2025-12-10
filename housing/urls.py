from django.urls import path
from . import views

app_name = 'housing'

urlpatterns = [
    path('', views.index, name='index'),
]

