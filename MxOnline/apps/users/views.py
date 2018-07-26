from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password, check_password

from .models import UserProfile,EmailVerifyRecord
from .forms import LoginForm,RegisterForm,ForgetPwdForm
from  utils.email_send import send_register_email

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

            send_register_email(user_name,"register")
            return render(request,'login.html')
        else:
            return render(request,'register.html',locals())
class LoginView(View):
    def get(self,request):
        return render(request,'login.html')

    def post(self,request):
        #实例化
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get('username', None)
            pass_word = request.POST.get('password', None)
            # 成功返回user对象，否则None
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return render(request, 'index.html')
            else:
                return render(request, 'login.html', {'msg':'用户名或密码错误','login_form':login_form})

        else:
            return render(request,'login.html',{'login_form':login_form})


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
    def get(self,request):
        pass