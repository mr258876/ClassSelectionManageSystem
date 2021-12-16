from os import name
from django.urls import path
from . import apis, views


urlpatterns = [
    path('', views.mgmt_home, name="mgmt_home"),
    path('<slug:operation>/', views.switch_operation, name="switch_operation"),
    path('add_user/', views.add_user, name="add_user"),
    path('mod_user/', views.mod_user, name="mod_user"),
    path('add_dept/', views.add_dept, name="add_dept"),
    path('mod_dept/', views.mod_dept, name="mod_dept"),
    path('mod_dept/<slug:dept_no>', views.mod_dept_info, name="mod_dept_info"),
    path('semester_settings/', views.semester_settings, name="semester_settings"),
    
    path('apis/add_user', apis.add_user_api, name='add_user_api'),
    path('apis/import_user', apis.import_user_api, name='import_user_api'),
    path('apis/csv_phrase', apis.csv_phrase_api, name='csv_phrase_api'),
    path('apis/search_user_api', apis.search_user_api, name='search_user_api'),
    path('apis/mod_user_api', apis.mod_user_api, name='mod_user_api'),
    path('apis/add_dept_api', apis.add_dept_api, name='add_dept_api'),
    path('apis/mod_dept_api', apis.mod_dept_api, name='mod_dept_api'),
    path('apis/search_dept_api', apis.search_dept_api, name='search_dept_api'),
    path('apis/add_semester_api', apis.add_semester_api, name='add_semester_api'),
    path('apis/mod_semester_api', apis.mod_semester_api, name='mod_semester_api'),
    path('apis/search_semester_api', apis.search_semester_api, name='search_semester_api'),
    path('apis/get_semester_api', apis.get_semester_api, name='get_semester_api'),
]