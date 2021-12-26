"""scss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from course.views import *
from course.apis import *

urlpatterns = [
    path('', home, name="course"),
    path('elect', elect, name="elect"),
    path('my_classes', my_classes, name="my_classes"),

    path('class_student/<slug:class_id>', class_student, name="class_student"),
    # path('teacher/create_course', create_course, name="create_course"),
    # path('teacher/view_detail/<int:course_id>', view_detail, name="view_detail"),
    # path('teacher/create_schedule/<int:course_id>', create_schedule, name="create_schedule"),
    # path('teacher/delete_schedule/<int:schedule_id>', delete_schedule, name="delete_schedule"),
    # path('teacher/score/<int:pk>', ScoreUpdateView.as_view(), name="score"),
    # path('teacher/handle_course/<int:course_id>/<int:handle_kind>', handle_course, name="handle_course"),

    # path('student/view/<slug:view_kind>', view_course, name="view_course"),
    # path('student/operate/<int:course_id>/<slug:operate_kind>', operate_course, name="operate_course"),

    # path('student/evaluate/<int:pk>', RateUpdateView.as_view(), name="evaluate"),
    # path('student/view_detail/<int:pk>', StudentCourseDetailView.as_view(), name="sview_detail"),

    path('apis/search_class_api', search_class_api, name='search_class_api'),
    path('apis/search_course_api', search_course_api, name='search_course_api'),
    path('apis/select_class_api', select_class_api, name='select_class_api'),
    path('apis/selected_class_api', selected_class_api, name='selected_class_api'),
    path('apis/teached_class_api', teached_class_api, name='teached_class_api'),
    path('apis/get_class_student_api', get_class_student_api, name='get_class_student_api'),
    path('apis/assign_student_to_class_api', assign_student_to_class_api, name='assign_student_to_class_api'),
    path('apis/score_student_api', score_student_api, name='score_student_api'),
    path('apis/add_course_api', add_course_api, name='add_course_api'),
    path('apis/mod_course_api', mod_course_api, name='mod_course_api'),
    path('apis/add_class_api', add_class_api, name='add_class_api'),
    path('apis/mod_class_api', mod_class_api, name='mod_class_api'),
    path('apis/del_course_api', mod_course_api, name='del_course_api'),
    path('apis/add_schedule_api', add_schedule_api, name='add_schedule_api'),
    path('apis/mod_schedule_api', mod_schedule_api, name='mod_schedule_api'),
    path('apis/del_schedule_api', del_schedule_api, name='del_schedule_api'),
    path('apis/get_semesters_api', get_semesters_api, name='get_semesters_api'),
]
