import json

from django.shortcuts import render,redirect,render_to_response
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from pure_pagination import Paginator,PageNotAnInteger

from .models import UserProfile,EmailVerifyRecord,Banner
from .forms import LoginForm,RegisterForm,ForgetPwdForm,ModifyPwdForm,UploadImageForm,UserInfoForm
from  utils.email_send import send_register_email
from operation.models import UserCourse,UserFavorite,UserMessage
from course.models import CourseOrg,Teacher,Course
#邮箱和用户名都可以登录
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))

            # django的后台中密码加密：所以不能password==password
            # UserProfile继承的AbstractUser中有def check_password(self, raw_password):
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class RegisterView(View):
    def get(self,request):
        register_form = RegisterForm()
        return render(request,'register.html',locals())

    def post(self,request):

        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            msg = ''
            user_name = request.POST.get('email',None)
            user = UserProfile.objects.filter(email=user_name)
            if user:
                msg = "用户名已存在"
                return render(request,'register.html',locals())

            pass_word = request.POST.get('password',None)
            user_profile = UserProfile.objects.create_user(user_name,user_name,make_password(pass_word),is_active=False)

            #写入欢迎注册消息
            message = UserMessage()
            message.user = user_profile
            message.message = "欢迎注册"
            message.save()
            #发送邮件
            send_register_email(user_name,"register")
            return redirect('login')
        else:
            return render(request,'register.html',locals())
class LoginView(View):
    def get(self,request):
        redirect_url = request.GET.get('next','/')
        return render(request,'login.html',locals())

    def post(self,request):
        #实例化
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get('username', None)
            pass_word = request.POST.get('password', None)
            # 成功返回user对象，否则None
            user = authenticate(username=user_name, password=pass_word)
            url = request.POST.get('next','')
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(url)
            else:
                return render(request, 'login.html', {'msg':'用户名或密码错误','login_form':login_form})

        else:
            return render(request,'login.html',{'login_form':login_form})


class LogoutView(View):
    '''用户登出'''
    def get(self,request):
        logout(request)
        return redirect('index')

class ActiveUserView(View):
    def get(self,request,active_code):
        # 查询邮箱验证记录是否存在
        all_record = EmailVerifyRecord.objects.filter(code=active_code)

        if all_record:
            for record in all_record:
                # 获取到对应的邮箱
                email = record.email
                # 查找到邮箱对应的user
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
                return render(request, "login.html", )
        # 验证码不对的时候跳转到激活失败页面
        return render(request,'login.html',{"msg":"链接已失效"})


class ForgetPwdView(View):
    """
    忘记密码
    """
    def get(self,request):
        forget_form = ForgetPwdForm()
        return render(request,'forgetpwd.html',{'forget_form':forget_form})

    def post(self,request):
        forget_form = ForgetPwdForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email',None)
            try:
                if UserProfile.objects.get(email=email):
                    send_register_email(email,'forget')
                    return render(request,'login.html',{"msg":"重置密码邮件已发送,请注意查收"})
            except:
                return render(request,'forgetpwd.html',{"msg":"该邮箱未注册"})
        else:
            return render(request,'forgetpwd.html',{'forget_form':forget_form})


class ResetView(View):
    '''重置密码'''
    def get(self,request,active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request,'password_reset.html',{'email':email})
        else:
            return render(request,'forgetpwd.html',{'msg':'激活链接已失效'})


class ModifyPwdView(View):
    '''修改密码'''
    def post(self,request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1',None)
            pwd2 = request.POST.get('password2',None)
            email = request.POST.get('email',None)
            if pwd1 != pwd2:
                msg = "密码不一致！"
                return render(request,'password_reset.html',locals())
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()
            return render(request, "login.html")
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", locals())


class UserInfoView(LoginRequiredMixin,View):
    '''用户个人信息'''
    login_url = 'login'
    redirect_field_name = 'next'
    def get(self,request):
        return render(request,'usercenter-info.html',{})

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class UploadImageView(LoginRequiredMixin,View):
    login_url = 'login'
    redirect_field_name = 'next'
    def post(self,request):
    # 这时候用户上传的文件就已经被保存到imageform了 ，为modelform添加instance值表示保存到哪个对象
        image_form = UploadImageForm(request.POST,request.FILES,instance=request.user)
        if image_form.is_valid():
            #modelForm可以直接保存
            image_form.save()
        # 取出cleaned data中的值,一个dict
        #     image = image_form.cleaned_data['image']
        #     request.user.image = image
        #     request.user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(View):
    """
    个人中心修改用户密码
    """
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail","msg":"密码不一致"}',  content_type='application/json')
            user = request.user
            user.password = make_password(pwd2)
            user.save()

            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(View):
    def get(self,request):
        email = request.GET.get('email','')
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已存在"}', content_type='application/json')

        send_register_email(email, 'update_email')
        return HttpResponse('{"status":"success"}', content_type='application/json')


class UpdateEmailView(View):
    def post(self,request):
        email = request.POST.get("email", "")
        code = request.POST.get("code", "")

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码无效"}', content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    '''我的课程'''
    login_url = 'login'
    redirect_field_name = 'next'
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html", {
            "user_courses":user_courses,
        })


class MyFavOrgView(LoginRequiredMixin,View):
    '''我收藏的课程机构'''
    login_url = 'login'
    redirect_field_name = 'next'

    def get(self, request):
        fav_orgs = UserFavorite.objects.filter(user=request.user,fav_type=2)
        org_list = []
        for fav_org in fav_orgs:
            # 取出fav_id也就是机构的id。
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, "usercenter-fav-org.html", {
            "org_list": org_list,
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    '''我收藏的授课讲师'''
    login_url = 'login'
    redirect_field_name = 'next'
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, "usercenter-fav-teacher.html", {
            "teacher_list": teacher_list,
        })


class MyFavCourseView(LoginRequiredMixin,View):
    """
    我收藏的课程
    """

    login_url = 'login'
    redirect_field_name = 'next'
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)

        return render(request, 'usercenter-fav-course.html', {
            "course_list":course_list,
        })


class MyMessageView(LoginRequiredMixin,View):
    '''我的消息'''

    login_url = 'login'
    redirect_field_name = 'next'
    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)

        for message in all_messages:
            message.has_read = True
            message.save()
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_messages, 4, request=request)
        messages = p.page(page)
        return render(request,'usercenter-message.html',{
            "messages":messages,
        })


class IndexView(View):
    def get(self,request):
        # 轮播图
        all_banners = Banner.objects.all().order_by('index')
        # 课程
        courses = Course.objects.filter(is_banner=False)[:6]
        # 轮播课程
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        # 课程机构
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs,
        })


def page_not_found(request):
    #404处理
    response = render_to_response('404.html')
    return response


def page_error(request):
    #500处理

    response = render_to_response('500.html')
    return response