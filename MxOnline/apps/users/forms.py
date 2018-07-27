from django import forms
from captcha.fields import CaptchaField

class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(min_length=6,required=True)


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True,min_length=6)
    # 验证码，字段里面可以自定义错误提示信息
    captcha = CaptchaField()


class ForgetPwdForm(forms.Form):
    '''忘记密码'''
    email = forms.EmailField(required=True)
    # 应用验证码 自定义错误输出key必须与异常一样
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class ModifyPwdForm(forms.Form):
    '''重置密码'''
    password1 = forms.CharField(required=True, min_length=6)
    password2 = forms.CharField(required=True, min_length=6)