import re

from django import forms

from operation.models import UserAsk
# class UserAskForm(forms.Form):
#     name = forms.CharField(required=True,min_length=2,max_length=20)
#     phone = forms.CharField(required=True,min_length=11,max_length=11)
#     course_name = forms.CharField(required=True,max_length=5)

class UserAskForm(forms.ModelForm):
    #addtime = ...可以添加字段
    class Meta:
        model = UserAsk
        fields = ['name','mobile','course_name']
    #验证手机号码
    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        p = re.compile("^1[358]\d{9}$|^147\d{8}$|^176\d{8}$")
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError("手机号码非法",code="mobile is invalid")
