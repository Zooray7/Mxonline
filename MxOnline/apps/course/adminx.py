import xadmin

from .models import Course, Lesson, Video, CourseResource

class LessonInline(object):
    model = Lesson
    extra = 0



class CourseAdmin(object):
    '''课程'''

    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']

    inlines = [LessonInline]
    style_fields = {"detail":"ueditor"}
    import_excel = True

    def queryset(self):
        return super().queryset().filter(is_banner=False)

    def post(self, request, *args, **kwargs):
        #  导入逻辑
        if 'excel' in request.FILES:
            pass
        return super(CourseAdmin, self).post(request, args, kwargs)



class LessonAdmin(object):
    '''章节'''

    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    # 这里course__name是根据课程名称过滤
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    '''视频'''

    list_display = ['lesson', 'name', 'add_time','learn_times']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time','learn_times']


class CourseResourceAdmin(object):
    '''课程资源'''

    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course__name', 'name', 'download', 'add_time']

class BannerCourse(Course):
    class Meta:
        verbose_name = '轮播课程'
        verbose_name_plural = verbose_name
        #设置proxy = true会具有model的功能，但不会生成表
        proxy = True


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']

    inlines = [LessonInline]

    def queryset(self):
        return super().queryset().filter(is_banner=True)


# 将管理器与model进行注册关联
xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse,BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
