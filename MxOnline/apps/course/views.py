from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from pure_pagination import Paginator,PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Course,CourseResource,Video
from operation.models import UserFavorite,CourseComments,UserCourse

class CourseListView(View):
    def get(self,request):
        all_courses = Course.objects.all().order_by("-add_time")

        hot_courses = Course.objects.all().order_by("-click_nums")[:3]

        current_page = 'course'
        #课程排序
        sort = request.GET.get('sort','')
        if sort:
            if sort == "students":
                all_courses = all_courses.order_by("-students")
            elif sort == "hot":
                all_courses = all_courses.order_by("-click_nums")
        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 这里指从all_orgs中取五个出来，每页显示3个
        p = Paginator(all_courses, 3, request=request)
        courses = p.page(page)
        return render(request,'course-list.html',{
            "all_courses":courses,
            "sort":sort,
            "hot_courses":hot_courses,
            "current_page": current_page,
        })


class CourseDetailView(View):
    def get(self,request,course_id):
        course = Course.objects.get(id=int(course_id))

        #增加课程点击数
        course.click_nums += 1
        course.save()

        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user,fav_id=course.id,fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user,fav_id=course.course_org.id,fav_type=2):
                has_fav_org = True

        tag = course.tag
        if tag:
            # 需要从1开始不然会推荐自己
            relate_courses = Course.objects.filter(tag=tag)[1:2]
        else:
            relate_courses = []
        return render(request,'course-detail.html',{
            "course":course,
            "relate_courses":relate_courses,
            "has_fav_course":has_fav_course,
            "has_fav_org":has_fav_org,
        })


class CourseInfoView(LoginRequiredMixin,View):
    """
    课程章节信息
    """
    #使用的命名空间，也可以写url地址
    login_url = 'login'
    redirect_field_name = 'redirect_to'
    def get(self,request,course_id):
        course = Course.objects.get(id=int(course_id))

        user_courses = UserCourse.objects.filter(user=request.user,course=course)
        if not user_courses:
            user_course = UserCourse.objects.create(user=request.user,course=course)

        #选出学了这门课的学生关系
        user_courses = UserCourse.objects.filter(course=course)
        #学习这门课的所有用户id
        user_ids =[user_course.user.id for user_course in user_courses]
        #所有用户学习的课程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        #所有课程id
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        #去掉列表里一样的课程id
        course_ids = list(set(course_ids))

        #删除本课程id
        course_ids.remove(int(course_id))
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, "course-video.html", {
            "course": course,
            "course_resources":all_resources,
            "relate_courses":relate_courses,

        })


class CourseCommentView(LoginRequiredMixin,View):
    """
    课程评论信息
    """
    login_url = 'login'
    redirect_field_name = 'redirect_to'
    def get(self,request,course_id):
        course = Course.objects.get(id=int(course_id))
        # 选出学了这门课的学生关系
        user_courses = UserCourse.objects.filter(course=course)
        # 学习这门课的所有用户id
        user_ids = [user_course.user.id for user_course in user_courses]
        # 所有用户学习的课程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 所有课程id
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        # 去掉列表里一样的课程id
        course_ids = list(set(course_ids))

        # 删除本课程id
        course_ids.remove(int(course_id))
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]

        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all()
        return render(request, "course-comment.html", {
            "course": course,
            "course_resources":all_resources,
            "all_comments":all_comments,
            "relate_courses":relate_courses,
        })


#添加评论
class AddCommentsView(View):
    '''用户评论'''
    def post(self, request):
        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        course_id =request.POST.get('course_id',0)
        comments = request.POST.get('comments','')
        if int(course_id) > 0 and comments:
            course = Course.objects.get(id=int(course_id))
            #实例化一个course_comments对象
            course_comment = CourseComments()
            course_comment.course = course
            course_comment.comments = comments
            course_comment.user = request.user
            course_comment.save()
            return HttpResponse('{"status":"success", "msg":"评论成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"评论失败"}', content_type='application/json')


class VideoPlayView(LoginRequiredMixin,View):
    """
    视频播放页面
    """
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))

        course = video.lesson.course
        # 查询用户是否开始学习了该课，如果还未学习则，加入用户课程表
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 选出学了这门课的学生关系
        user_courses = UserCourse.objects.filter(course=course)
        # 学习这门课的所有用户id
        user_ids = [user_course.user.id for user_course in user_courses]
        # 所有用户学习的课程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 所有课程id
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        # 去掉列表里一样的课程id
        course_ids = list(set(course_ids))

        course_id = course.id
        # 删除本课程id
        course_ids.remove(int(course_id))
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        # 查询课程资源
        all_resources = CourseResource.objects.filter(course=course)

        return render(request, "course-play.html", {
            "course": course,
            "course_resources": all_resources,
            "relate_courses": relate_courses,
            "video":video,
        })