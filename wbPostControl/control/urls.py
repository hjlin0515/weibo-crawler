from django.conf.urls import patterns,url
from control import views

urlpatterns = [
    url(r'^$',views.index,name='index'),
    url(r'^add_account/$',views.add_account,name='add_account'),
    url(r'^account_status/(?P<username>[\w]+)/$',views.account_status,name='account_status'),
    url(r'^delete_account/$',views.delete_account,name='delete_account'),
]
