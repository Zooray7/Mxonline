from django.urls import path, re_path

from .views import CourseListView
app_name = "course"

urlpatterns = [
    #课程列表页
    path('list',CourseListView.as_view(),name="course_list")
]