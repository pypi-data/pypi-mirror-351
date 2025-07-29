开始使用

**1、在INSTALLED_APPS中添加django_sohoui**

```
INSTALLED_APPS = [
    'django_sohoui',
    'django.contrib.admin',
    ....
]
```

**2、执行makemigrations**

```
python manage.py makemigrations
python manage.py migrate      
```      

**3、 在TEMPLATES中添加context_processors   **      

```
'context_processors': [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    ## 添加custom_context
    'django_sohoui.context_processors.custom_context',
]
```

**4、 在project/urls.py中添加django_sohoui**
```
urlpatterns = [
    path('admin/', admin.site.urls),
    ## 添加django_sohoui
    path('django_sohoui/', include('django_sohoui.urls')),
]

```
**5、 在project/settings.py中添加LOGIN_BG_IMAGE(自定义登录页背景图片)**

```
SOHO_LOGIN_BG_IMAGE = '/static/custom/images/logo_bg.jpg'
```


**6、 在project/settings.py中添加SOHO_MENU_LIST**

```
SOHO_MENU_LIST = {
    'show_system_menu': True, ## 是否显示系统菜单
    'models':[
        {
            'name': '苏豪菜单模块',
            'models': [
                {
                    'name': 'System菜单设置',
                    'admin_url': '/admin/django_sohoui/adminmenus/'
                },
                {
                    'name': 'System菜单设置1',
                    'admin_url': '/admin/django_sohoui/adminmenus/',
                    #自定义页面添加权限，admin model不需要指定权限
                    'permission': 'app.can_admin_sohoui_site'
                }
            ]
        },
    ]
}
```