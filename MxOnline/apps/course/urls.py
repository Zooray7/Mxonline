from django.urls import path, re_path

from .views import CourseListView,CourseDetailView,CourseInfoView,CourseCommentView,AddCommentsView
app_name = "course"

urlpatterns = [
    #课程列表页
    path('list/',CourseListView.as_view(),name="course_list"),
    #课程详情
    re_path('detail/(?P<course_id>\d+)',CourseDetailView.as_view(),name="course_detail"),
    #课程章节信息
    re_path('info/(?P<course_id>\d+)', CourseInfoView.as_view(), name="course_info"),
    #课程评论页面
    re_path('comment/(?P<course_id>\d+)', CourseCommentView.as_view(), name="course_comment"),
    #添加评论
    path('add_comment/', AddCommentsView.as_view(), name="add_comment"),
]