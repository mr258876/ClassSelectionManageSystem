from django.urls import path
from user import views


urlpatterns = [
    path('login/', views.home, name="login"),
    path('login/<slug:role>', views.login, name="login"),
    path('register/', views.register, name="register"),

    path('update_info/', views.update_info, name="update_info"),
    path('update_security/', views.update_security, name="update_security"),

    path('logout/', views.logout, name="logout"),
]
