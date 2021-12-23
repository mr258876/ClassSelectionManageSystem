from os import name
from .models import *
from mgmt.util import get_current_semester, get_semester_ids

from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction

import json

#######################################
# 权限测试器

# 用户具有管理权限
def user_mgmtable(user):
    return user.role == 'dept' or user.is_superuser

# 用户具有教师及以上权限
def user_teacher_and_above(user):
    return user.role == 'teacher' or (user.role == 'dept' and hasattr(user, 'department')) or user.is_superuser

# 管理员测试器
def user_is_admin(user):
    return user.is_superuser

# 院系权限测试器
def user_is_dept(user):
    return user.role == 'dept' and hasattr(user, 'department')

# 教师权限测试器
def user_is_teacher(user):
    return user.role == 'teacher'

# 学生权限测试器
def user_is_student(user):
    return user.role == 'student'


#######################################
# 课程查询、基础操作API
# TODO
# 课程班级查找API
@login_required
@require_http_methods(['POST'])
@ensure_csrf_cookie
def search_class_api(request):
    kList = ['courseId', 'courseName']

    k = request.POST.get("searchMode", "")
    sem = request.POST.get("searchSemester", "")
    kw = request.POST.get("keyword", "")
    pN = request.POST.get("page", 1)
    iPP = request.POST.get("itemPerPage", 25)

    if sem == 'current':
        sem = get_current_semester().id
    
    sem_list = Semester.objects.filter(id=sem)
    if len(sem_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "学期不存在", "data": ""})
    semester = sem_list[0]
    
    if k and sem and k in kList:
        qSet = None
        if k == 'courseId':
            qSet = Class.objects.filter(course__id__contains=kw).filter(semester=semester).order_by('id')
        elif k == 'courseName':
            qSet = Class.objects.filter(course__name__contains=kw).filter(semester=semester).order_by('id')
        else:
            return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})
        p = Paginator(qSet, iPP)
        d = []
        for c in p.get_page(pN).object_list:
            d.append([c.id, c.course.id, c.course.name, c.course.dept.dept_name, c.course.credit, c.grade_type, c.teacher.name])
        plist = p.get_elided_page_range(pN, on_each_side=2, on_ends=1)
        pl = json.dumps(list(plist))
        pl = json.loads(pl)
        return JsonResponse({"success": True, "code": 200, "message":"操作成功", "data":{'classes':d, 'plist':pl, 'page':pN, 'total': len(qSet)}})
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})


# 课程查找API
@login_required
@require_http_methods(['POST'])
@ensure_csrf_cookie
def search_course_api(request):
    kList = ['courseId', 'courseName']

    k = request.POST.get("searchMode", "")
    kw = request.POST.get("keyword", "")
    pN = request.POST.get("page", 1)
    iPP = request.POST.get("itemPerPage", 25)
    
    if k and k in kList:
        qSet = None
        if k == 'courseId':
            qSet = Course.objects.filter(id__contains=kw).order_by('id')
        elif k == 'courseName':
            qSet = Course.objects.filter(name__contains=kw).order_by('id')
        else:
            return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})
        p = Paginator(qSet, iPP)
        d = []
        for c in p.get_page(pN).object_list:
            d.append([c.id, c.name, c.dept.dept_name, c.credit])
        plist = p.get_elided_page_range(pN, on_each_side=2, on_ends=1)
        pl = json.dumps(list(plist))
        pl = json.loads(pl)
        return JsonResponse({"success": True, "code": 200, "message":"操作成功", "data":{'course':d, 'plist':pl, 'page':pN, 'total': len(qSet)}})
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})


# 选课/退课API
@login_required
@user_passes_test(user_is_student)
@require_http_methods(['POST'])
@ensure_csrf_cookie
@transaction.atomic
def select_class_api(request):
    operation_list = ['elect', 'withdraw']

    operation = request.POST.get("operation", "")
    class_id = request.POST.get("class_id", "")

    if operation and class_id and operation in operation_list:
        student_class_record_list = StudentCourseInfo.objects.filter(student=request.user.student)
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})
    
    # 选课
    if operation == 'elect':
        # 若课程id不存在则报错
        class_list = Class.objects.select_for_update().filter(id=class_id)
        if len(class_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message":"课程不存在", "data":""})
        class_course = class_list[0]

        # 不在选课时间内报错
        if datetime.datetime.now() < class_course.semester.select_start or datetime.datetime.now() > class_course.semester.select_start:
            return JsonResponse({"success": False, "code": 400, "message":"当前不在选课时间范围内", "data":""})

        # 课程已满则报错
        if class_course.attends >= class_course.amount:
            return JsonResponse({"success": False, "code": 400, "message":"课程已满", "data":""})
        
        # 若已选相同课程则报错
        selected_course_list = student_class_record_list.filter(class__course=class_course)
        if len(selected_course_list) > 0:
            return JsonResponse({"success": False, "code": 400, "message":"已选相同课程", "data":""})
        
        # 若先修课不满足（没修/没过/这学期没选）则报错
        requirements = class_course.requirements.all()
        for r in requirements:
            course_record = student_class_record_list.filter(courseClass__course=r)
            pass_record = course_record.filter(grade__gte=60)
            if len(pass_record) > 0:
                continue
            
            select_record = course_record.filter(courseClass__course__semester=get_current_semester())
            if len(select_record) > 0:
                continue
            else:
                return JsonResponse({"success": False, "code": 400, "message":"先修课不满足", "data":r})
        
        try:
            record = StudentCourseInfo(student=request.user.student, classCourse=class_course, grade=None, grade_type=class_course.grade_type)
            record.save()
            class_course.attends += 1
            class_course.save()
        except Exception as e:
            return JsonResponse({"success": False, "code": 400, "message": "选课失败", "data": str(e)})
        return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})
    # 退课
    elif operation == 'withdraw':
        record_list = student_class_record_list.filter(classCourse__id=class_id)
        # 未选该课程报错
        if len(record_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message":"未参加该课程", "data":""})
        class_record = record_list[0]

        # 不在选课时间内报错
        if datetime.datetime.now() < class_record.classCourse.semester.select_start or datetime.datetime.now() > class_record.classCourse.semester.select_start:
            return JsonResponse({"success": False, "code": 400, "message":"当前不在选课时间范围内", "data":""})
        
        try:
            class_record.courseClass.attends -= 1
            class_record.courseClass.save()
            class_record.delete()
        except Exception as e:
            return JsonResponse({"success": False, "code": 400, "message": "退课失败", "data": str(e)})
        return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})
    return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})

# TODO
# 查看已选课程API
@login_required
@require_http_methods(['POST'])
@ensure_csrf_cookie
@transaction.atomic
def selected_class_api(request):
    if request.user.role == 'student':
        student = request.user.student
    else:
        sid = request.POST.get("student_id", "")
        if not sid:
            return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})
        student_list = Student.objects.filter(user__uid=sid).only()
        if len(student_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message": "学生不存在", "data": ""})

    pN = request.POST.get("page", 1)
    iPP = request.POST.get("itemPerPage", 25)

    sem = request.POST.get("searchSemester", "")
    if sem == 'current':
        sem = get_current_semester().id
    else:
        sem_list = Semester.objects.filter(id=sem)
        if len(sem_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message": "学期不存在", "data": ""})
        semester = sem_list[0]

    classes = StudentCourseInfo.objects.filter(student=student).filter(classCourse__semester=semester)
    p = Paginator(classes, iPP)
    # json_response = serializers.serialize('json', list(p.object_list))
    d = json.dumps(list(p.page(pN)))
    d = json.loads(d)
    plist = p.get_elided_page_range(pN, on_each_side=2, on_ends=1)
    pl = json.dumps(list(plist))
    pl = json.loads(pl)
    return JsonResponse({"success": False, "code": 400, "message": "", "data": ""})


# 将学生加入课程API
@login_required
@user_passes_test(user_teacher_and_above)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def assign_student_to_class_api(request):
    sid = request.POST.get("student_id", "")
    cid = request.POST.get("class_id", "")

    student_list = Student.objects.filter(user__uid=sid).only()
    if len(student_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "学生不存在", "data": ""})
    
    class_list = Class.objects.filter(id=cid).only()
    if len(class_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "课程不存在", "data": ""})
    class_course = class_list[0]

    try:
        record = StudentCourseInfo(student=student_list[0], classCourse=class_course, grade=None, grade_type=class_course.grade_type)
        record.save()
        class_course.attends += 1
        class_course.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "选课失败", "data": str(e)})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})


#######################################
# 课程管理API

# 添加课程API
@login_required
@user_passes_test(user_mgmtable)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def add_course_api(request):
    c_id = request.POST.get("course_id", "")
    c_name = request.POST.get("course_name", "")
    c_description = request.POST.get("course_description", "")
    c_credit = request.POST.get("course_credit", "")
    c_dept = request.POST.get("course_dept", "")

    if c_id and c_name and c_dept and c_credit != "":
        pass
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})

    if request.user.is_superuser:
        dept_list = Department.objects.filter(dept_no=c_dept)
        if len(dept_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message":"院系ID不存在", "data":""})
        c_dept = dept_list[0]
    else:
        c_dept = request.user.department
    
    try:
        course = Course(id=c_id, name=c_name, description=c_description, credit=c_credit, dept=c_dept)
        course.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "创建失败", "data": str(e)})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})

# TODO
# 修改课程API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def mod_course_api(request):
    d_no = request.POST.get("deptId", "")
    d_name = request.POST.get("deptName", "")
    d_user = request.POST.get("deptUser", "")

    dept_set = Department.objects.filter(dept_no=d_no)
    if len(dept_set) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "院系ID不存在", "data": ""})

    user_set = User.objects.filter(uid=d_user)
    if len(dept_set) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "用户id不存在", "data": ""})
    if user_set[0].role != 'dept':
        return JsonResponse({"success": False, "code": 400, "message": "用户权限错误", "data": ""})

    try:
        dept = dept_set[0]
        dept.dept_no = d_no
        dept.dept_name = d_name
        dept.dept_user = user_set[0]
        dept.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "创建失败", "data": str(e)})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})


# 添加班级API
@login_required
@user_passes_test(user_mgmtable)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def add_class_api(request):
    c_name = request.POST.get("class_name", "")
    c_course_id = request.POST.get("class_course_id", "")
    c_teacher_uid = request.POST.get("class_teacher_uid", "")
    c_semester_id = request.POST.get("class_semester_id", "")
    c_amount = request.POST.get("class_amount", "")
    c_grade_type = request.POST.get("class_grade_type", "")

    if c_course_id and c_teacher_uid and c_semester_id and c_amount and c_grade_type in ('PF', 'SC', '13'):
        pass
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})

    course_list = Course.objects.filter(id=c_course_id).only()
    if len(course_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message":"课程不存在", "data":""})
    # 若为院系用户且课程院系不对应
    if not request.user.is_superuser:
        if request.user.department != course_list[0].dept:
            return JsonResponse({"success": False, "code": 400, "message":"权限不足", "data":""})
    teacher_list = Teacher.objects.filter(user__uid=c_teacher_uid).only()
    if len(teacher_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message":"教师不存在", "data":""})
    semester_list = Semester.objects.filter(id=c_semester_id).only()
    if len(semester_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message":"学期不存在", "data":""})

    try:
        courseClass = Class(name=c_name, course=course_list[0], teacher=teacher_list[0], semester=semester_list[0], amount=c_amount, grade_type=c_grade_type)
        courseClass.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "创建失败", "data": str(e)})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})

# TODO
# 修改班级API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def mod_class_api(request):
    d_no = request.POST.get("deptId", "")
    d_name = request.POST.get("deptName", "")
    d_user = request.POST.get("deptUser", "")

    dept_set = Department.objects.filter(dept_no=d_no)
    if len(dept_set) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "院系ID不存在", "data": ""})

    user_set = User.objects.filter(uid=d_user)
    if len(dept_set) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "用户id不存在", "data": ""})
    if user_set[0].role != 'dept':
        return JsonResponse({"success": False, "code": 400, "message": "用户权限错误", "data": ""})

    try:
        dept = dept_set[0]
        dept.dept_no = d_no
        dept.dept_name = d_name
        dept.dept_user = user_set[0]
        dept.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "创建失败", "data": str(e)})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})


# 删除课程/班级API
@login_required
@user_passes_test(user_mgmtable)
@require_http_methods(['POST'])
@ensure_csrf_cookie
@transaction.atomic
def del_course_api(request):
    operation_list = {"del_course", "del_class"}

    c_id = request.POST.get("courseId", "")
    operation = request.POST.get("operation", "")

    if operation not in operation_list:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})
    elif operation == "del_course":
        c_list = Course.objects.filter(id=c_id).only()
    else:
        c_list = Class.objects.filter(id=c_id).only()

    if len(c_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message":"课程或班级不存在", "data":""})
    
    c = c_list[0]
    try:
        c.delete()
    except:
        return JsonResponse({"success": False, "code": 400, "message":"删除失败", "data":""})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})

# TODO
# 创建Schedule API
@login_required
@user_passes_test(user_mgmtable)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def add_schedule_api(request):
    c_id = request.POST.get("course_id", "")
    c_name = request.POST.get("course_name", "")
    c_description = request.POST.get("course_description", "")
    c_credit = request.POST.get("course_credit", "")
    c_dept = request.POST.get("course_dept", "")

    if c_id and c_name and c_description and c_credit != "":
        pass
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})

    if request.user.is_superuser:
        dept_list = Department.objects.filter(dept_no=c_dept)
        if len(dept_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message":"院系ID不存在", "data":""})
        c_dept = dept_list[0]
    else:
        c_dept = request.user.department
    
    try:
        course = Course(id=c_id, name=c_name, description=c_description, credit=c_credit, dept=c_dept)
        course.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "创建失败", "data": str(e)})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})

# TODO
# 修改Schedule API
@login_required
@user_passes_test(user_mgmtable)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def mod_schedule_api(request):
    c_id = request.POST.get("course_id", "")
    c_name = request.POST.get("course_name", "")
    c_description = request.POST.get("course_description", "")
    c_credit = request.POST.get("course_credit", "")
    c_dept = request.POST.get("course_dept", "")

    if c_id and c_name and c_description and c_credit != "":
        pass
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})

    if request.user.is_superuser:
        dept_list = Department.objects.filter(dept_no=c_dept)
        if len(dept_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message":"院系ID不存在", "data":""})
        c_dept = dept_list[0]
    else:
        c_dept = request.user.department
    
    try:
        course = Course(id=c_id, name=c_name, description=c_description, credit=c_credit, dept=c_dept)
        course.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "创建失败", "data": str(e)})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})


# TODO
# 删除Schedule API
@login_required
@user_passes_test(user_mgmtable)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def del_schedule_api(request):
    c_id = request.POST.get("course_id", "")
    c_name = request.POST.get("course_name", "")
    c_description = request.POST.get("course_description", "")
    c_credit = request.POST.get("course_credit", "")
    c_dept = request.POST.get("course_dept", "")

    if c_id and c_name and c_description and c_credit != "":
        pass
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})

    if request.user.is_superuser:
        dept_list = Department.objects.filter(dept_no=c_dept)
        if len(dept_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message":"院系ID不存在", "data":""})
        c_dept = dept_list[0]
    else:
        c_dept = request.user.department
    
    try:
        course = Course(id=c_id, name=c_name, description=c_description, credit=c_credit, dept=c_dept)
        course.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "创建失败", "data": str(e)})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})


#######################################
# 杂项

# 获取所有学期名称及id
def get_semesters_api(request):
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": {'semesters': get_semester_ids()}})