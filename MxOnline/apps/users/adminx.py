import xadmin


from .models import EmailVerifyRecord,Banner
from xadmin import views


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

xadmin.site.register(EmailVerifyRecord,EmailVerifyRecordAdmin)


class BannerAdmin(object):
    list_display = ['title', 'image', 'url','index', 'add_time']
    search_fields = ['title', 'image', 'url','index']
    list_filter = ['title', 'image', 'url','index', 'add_time']

# 将基本配置管理与view绑定
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(Banner,BannerAdmin)