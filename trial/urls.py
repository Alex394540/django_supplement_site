from django.urls import path

from . import views

app_name = 'trial'
urlpatterns = [
    path('', views.index, name='index'),
    path('thanks/', views.success, name='success'),
    path('createuser/', views.createuser, name='createuser'),
    path('add_drug/', views.add_drug, name='add_drug'),
    path('ajax/change_amount', views.change_amount, name='change_amount'),
    path('statistics/', views.statistics, name='statistics'),
    path('operations/', views.operations, name='operations'),
    path('login/', views.log_in, name='log_in'),
    path('logout/', views.log_out, name='log_out'),
    path('product_page/', views.product_page, name='product_page'),
    path('ajax/get_categ/', views.stat_categ, name='stat_categ'),
    path('ajax/all_prod/', views.stat_prod, name='stat_prod'),
    path('ajax/stat_month/', views.stat_month, name='stat_month'),
    path('ajax/show_cat/', views.get_categories, name='show_cat'),
    path('ajax/show_prod/', views.get_products, name='show_prod'),
    path('ajax/show_docs/', views.get_doctors, name='show_docs'),
    path('ajax/show_man/', views.get_manufacturers, name='show_man'),
    path('ajax/save_changes/', views.save_changes, name='save_changes'),
    path('ajax/delete_product/', views.delete_product, name='delete_product'),
    path('ajax/filter_operations/', views.filter_operations, name='filter_operations'),
    path('register/', views.register, name='register'),
    path('add_doctor/', views.add_doctor, name='add_doctor'),
    path('site_settings/', views.site_settings, name='site_settings'),
    path('notifications/', views.notifications, name='notifications'),
    path('change_pass/', views.change_pass, name='change_pass'),
    path('ajax/user_info/', views.user_info, name='user_info'),
    path('ajax/delete_user/', views.delete_user, name='delete_user'),
    path('ajax/show_notifications/', views.show_notifications, name='show_notifications'),
    path('patient_account/', views.patient_account, name='patient_account'),
    path('order_details/', views.order_details, name='order_details'),
    path('orders/', views.orders, name='orders'),
    path('mark_completed/', views.mark_completed, name='mark_completed'),
]