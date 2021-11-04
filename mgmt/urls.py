from os import name
from django.urls import path
from . import apis, views


urlpatterns = [
    path('', views.mgmt_home, name="mgmt_home"),
    path('<slug:operation>/', views.switch_operation, name="switch_operation"),
    path('add_user/', views.add_user, name="add_user"),
    path('mod_user/', views.mod_user, name="mod_user"),
    path('set_selection_schedule', views.set_selection_schedule, name="set_selection_schedule"),
    
    path('apis/add_user', apis.add_user_api, name='add_user_api'),
    path('apis/import_user', apis.import_user_api, name='import_user_api'),
    path('apis/csv_phrase', apis.csv_phrase_api, name='csv_phrase_api'),
    path('apis/search_user_api', apis.search_user_api, name='search_user_api')
]