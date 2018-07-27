from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.generic.base import View
from pure_pagination import Paginator,PageNotAnInteger

from .models import CourseOrg,CityDict
from .forms import UserAskForm


class OrgView(View):
    def get(self,request):
        #取出所有课程机构
        all_orgs = CourseOrg.objects.all()

        category = request.GET.get('ct','')
        if category:
            all_orgs = all_orgs.filter(category=category)
        #热门机构
        hot_orgs = all_orgs.order_by('-click_nums')[:3]
        #机构数量
        org_nums = all_orgs.count()
        #取出所有城市
        all_cities = CityDict.objects.all()
        #字符串转成整数

        city_id = request.GET.get('city','')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        sort = request.GET.get('sort','')
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")

        #分页
        try:
            page = request.GET.get('page',1)
        except PageNotAnInteger:
            page = 1
        # 这里指从all_orgs中取五个出来，每页显示5个
        p = Paginator(all_orgs,5,request=request)
        orgs = p.page(page)

        return render(request,'org-list.html',{
            "all_orgs": orgs,
            "all_cities": all_cities,
            "org_nums": org_nums,
            "city_id":city_id,
            "category":category,
            "hot_orgs":hot_orgs,
            "sort":sort,
        })


class AddUserAskView(View):
    """
    用户添加咨询
    """
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            # 如果保存成功,返回json字符串,后面content type是告诉浏览器返回的数据类型
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            # 如果保存失败，返回json字符串,并将form的报错信息通过msg传递到前端
            return HttpResponse('{"status":"fail", "msg":"添加出错"}', content_type='application/json')


class OrgHomeView(View):
    """
    机构首页
    """

    def get(self,request,org_id):
        # 根据id找到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))

        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request,'org-detail-homepage.html',{
            "all_courses":all_courses,
            "all_teachers":all_teachers,
            "course_org":course_org
        })