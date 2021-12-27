from django.urls import path
from user import views


urlpatterns = [
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),

    path('update_info/', views.update_info, name="update_info"),
    path('update_password/', views.update_password, name="update_password"),
    path('update_email/', views.update_email, name="update_email"),

    path('logout/', views.logout, name="logout"),
]
