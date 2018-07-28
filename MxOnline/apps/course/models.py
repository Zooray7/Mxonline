from django.db import models

# Create your models here.

from datetime import datetime

from django.db import models

from organization.models import CourseOrg,Teacher

class Course(models.Model):
    DEGREE_CHOICES = (
        ("cj", "初级"),
        ("zj", "中级"),
        ("gj", "高级")
    )
    course_org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE, verbose_name="所属机构", null=True, blank=True)
    teacher = models.ForeignKey(Teacher, verbose_name="讲师",on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField("课程名",max_length=50)
    desc = models.CharField("课程描述",max_length=300)
    detail = models.TextField("课程详情")
    degree = models.CharField('难度',choices=DEGREE_CHOICES, max_length=2)
    learn_times = models.IntegerField("学习时长(小时数)",default=0)
    students = models.IntegerField("学习人数",default=0)
    fav_nums = models.IntegerField("收藏人数",default=0)
    image = models.ImageField("封面图",upload_to="courses/%Y/%m",max_length=100,null=True, blank=True)
    click_nums = models.IntegerField("点击数",default=0)
    category = models.CharField("课程类别",max_length=30,default="后端开发")
    tag = models.CharField("课程标签",max_length=10,default='')
    you_need_know = models.CharField("课程须知",max_length=300, default="一颗勤学的心是本课程必要前提", )
    teacher_tell = models.CharField("老师告诉你",max_length=300, default="按时交作业,不然叫家长")
    add_time = models.DateTimeField("添加时间",default=datetime.now,)

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = verbose_name

    def get_zj_nums(self):
        return self.lesson_set.all().count()

    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    def get_course_lesson(self):
        #获取课程所有章节
        return self.lesson_set.all()

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course,verbose_name='课程',on_delete=models.CASCADE)
    learn_times = models.IntegerField("学习时长(小时数)", default=100)
    name = models.CharField("章节名",max_length=100)
    add_time = models.DateTimeField("添加时间",default=datetime.now)

    class Meta:
        verbose_name = "章节"
        verbose_name_plural = verbose_name

    def get_lesson_video(self):
        #获取章节视频
        return self.video_set.all()

    def __str__(self):
       return '《{0}》课程的章节 >> {1}'.format(self.course, self.name)


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name="章节",on_delete=models.CASCADE)
    learn_times = models.IntegerField("学习时长(分钟数)", default=20)
    name = models.CharField("视频名",max_length=100)
    url = models.CharField("访问地址",max_length=200,default='https://www.imooc.com/learn/943')
    add_time = models.DateTimeField("添加时间", default=datetime.now)

    class Meta:
        verbose_name = "视频"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name="课程",on_delete=models.CASCADE)
    name = models.CharField("名称",max_length=100)
    download = models.FileField("资源文件",upload_to="course/resource/%Y/%m",max_length=100)
    add_time = models.DateTimeField("添加时间", default=datetime.now)

    class Meta:
        verbose_name = "课程资源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name