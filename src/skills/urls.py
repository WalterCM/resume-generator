from django.urls import path

from skills import views


app_name = 'skills'

urlpatterns = [
    path('create/', views.CreateSkillView.as_view(), name='create'),
    path('list/', views.ListSkillsView.as_view(), name='list'),
]
