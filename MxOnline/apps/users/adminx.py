import xadmin

from xadmin import views
# from xadmin.plugins.auth import UserAdmin
from .models import EmailVerifyRecord,Banner,UserProfile



# class UserProfileAdmin(UserAdmin):
#     pass


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


# 全局修改，固定写法
class GlobalSettings(object):
    # 修改title
    site_title = '地球后台管理界面'
    # 修改footer
    site_footer = '我的世界'
    # 收起菜单
    menu_style = 'accordion'

# 将title和footer信息进行注册
xadmin.site.register(views.CommAdminView,GlobalSettings)


class EmailVerifyRecordAdmin():
    list_display = ['code','email','send_type','send_time']
    search_fields = ['code','email','send_type']
    list_filter = ['code','email','send_type','send_time']
    # model_icon = 'fa fa-user'
    # ordering = ['send_time'] 排序
    #readonly_fields = ['']字段只读，不可以修改
    #exclude = ['']  不显示哪些，和readonly_fields冲突

    #relfield_style = 'fk-ajax'下拉框搜索，数据量过大时很有用，当有外键指向他，会以ajax方式加载,设在外键的里面
xadmin.site.register(EmailVerifyRecord,EmailVerifyRecordAdmin)


class BannerAdmin(object):
    list_display = ['title', 'image', 'url','index', 'add_time']
    search_fields = ['title', 'image', 'url','index']
    list_filter = ['title', 'image', 'url','index', 'add_time']

# 将基本配置管理与view绑定
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(Banner,BannerAdmin)
# xadmin.site.register(UserProfile, UserProfileAdmin)
