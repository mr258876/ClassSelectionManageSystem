from django.urls import path
from user import views


urlpatterns = [
    path('login/', views.home, name="login"),
    path('login/<slug:role>', views.login, name="login"),
    path('register/', views.register, name="register"),

    path('update/<slug:role>', views.update, name="update"),

    path('logout/', views.logout, name="logout"),
]
