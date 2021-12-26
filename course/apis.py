from os import name
from .models import *
from mgmt.util import get_current_semester, get_semester_ids, get_now_elect_semester

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
    kList = ['courseId', 'courseName', 'courseIdPrecise', 'teacherName']

    k = request.POST.get("searchMode", "")
    sem = request.POST.get("searchSemester", "")
    kw = request.POST.get("keyword", "")
    pN = request.POST.get("page", 1)
    iPP = request.POST.get("itemPerPage", 25)

    if not sem or sem == 'current':
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
        elif k == 'courseIdPrecise':
            qSet = Class.objects.filter(id=kw)
        elif k == 'teacherName':
            qSet = Class.objects.filter(teacher__name__contains=kw).filter(semester=semester).order_by('id')
        else:
            return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})
        p = Paginator(qSet, iPP)
        d = []
        for c in p.get_page(pN).object_list:
            d.append([c.id, c.course.id, c.course.name, c.name, c.course.dept.dept_name, c.course.credit, c.grade_type, c.teacher.name, c.attends, c.amount])
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
    kList = ['courseId', 'courseName', 'courseIdPrecise']

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
        elif k == 'courseIdPrecise':
            qSet = Course.objects.filter(id=kw)
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
        if datetime.datetime.now() < class_course.semester.select_start.replace(tzinfo=None) or datetime.datetime.now() > class_course.semester.select_end.replace(tzinfo=None):
            return JsonResponse({"success": False, "code": 400, "message":"当前不在选课时间范围内", "data":""})

        # 课程已满则报错
        if class_course.attends >= class_course.amount:
            return JsonResponse({"success": False, "code": 400, "message":"课程已满", "data":""})
        
        # 若已选相同课程则报错
        selected_course_list = student_class_record_list.filter(courseClass__course=class_course.course).filter(courseClass__semester=get_now_elect_semester())
        if len(selected_course_list) > 0:
            return JsonResponse({"success": False, "code": 400, "message":"已选相同课程", "data":""})
        
        # 若先修课不满足（没修/没过/这学期没选）则报错
        # requirements = class_course.requirements.all()
        # for r in requirements:
        #     course_record = student_class_record_list.filter(courseClass__course=r)
        #     pass_record = course_record.filter(grade__gte=60)
        #     if len(pass_record) > 0:
        #         continue
            
        #     select_record = course_record.filter(courseClass__course__semester=get_current_semester())
        #     if len(select_record) > 0:
        #         continue
        #     else:
        #         return JsonResponse({"success": False, "code": 400, "message":"先修课不满足", "data":r})
        
        try:
            record = StudentCourseInfo(student=request.user.student, courseClass=class_course, grade=None, grade_type=class_course.grade_type)
            record.save()
            class_course.attends += 1
            class_course.save()
        except Exception as e:
            return JsonResponse({"success": False, "code": 400, "message": "选课失败", "data": str(e)})
        return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})
    # 退课
    elif operation == 'withdraw':
        record_list = student_class_record_list.filter(courseClass__id=class_id)
        # 未选该课程报错
        if len(record_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message":"未参加该课程", "data":""})
        class_record = record_list[0]
        class_course = class_record.courseClass

        # 不在选课时间内报错
        if datetime.datetime.now() < class_course.semester.select_start.replace(tzinfo=None) or datetime.datetime.now() > class_course.semester.select_end.replace(tzinfo=None):
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
        student = student_list[0]

    pN = request.POST.get("page", 1)
    iPP = request.POST.get("itemPerPage", 25)

    sem = request.POST.get("searchSemester", "")
    if not sem or sem == 'current':
        semester = get_current_semester()
    else:
        sem_list = Semester.objects.filter(id=sem)
        if len(sem_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message": "学期不存在", "data": ""})
        semester = sem_list[0]

    classes = StudentCourseInfo.objects.filter(student=student).filter(courseClass__semester=semester)
    p = Paginator(classes, iPP)
    d = []
    for record in p.get_page(pN).object_list:
        c = record.courseClass
        d.append([c.id, c.course.id, c.course.name, c.name, c.teacher.name, c.attends, c.amount, record.grade])
    plist = p.get_elided_page_range(pN, on_each_side=2, on_ends=1)
    pl = json.dumps(list(plist))
    pl = json.loads(pl)
    return JsonResponse({"success": True, "code": 200, "message":"操作成功", "data":{'classes':d, 'plist':pl, 'page':pN, 'total': len(classes)}})


# TODO
# 查看我教的课API
@login_required
@require_http_methods(['POST'])
@user_passes_test(user_teacher_and_above)
@ensure_csrf_cookie
@transaction.atomic
def teached_class_api(request):
    if request.user.role == 'teacher':
        teacher = request.user.teacher
    else:
        tid = request.POST.get("teacher_id", "")
        if not tid:
            return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})
        teacher_list = Teacher.objects.filter(user__uid=sid).only()
        if len(teacher_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message": "学生不存在", "data": ""})
        teacher = teacher_list[0]

    pN = request.POST.get("page", 1)
    iPP = request.POST.get("itemPerPage", 25)

    sem = request.POST.get("searchSemester", "")
    if not sem or sem == 'current':
        semester = get_current_semester()
    else:
        sem_list = Semester.objects.filter(id=sem)
        if len(sem_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message": "学期不存在", "data": ""})
        semester = sem_list[0]

    classes = Class.objects.filter(teacher=teacher).filter(semester=semester)
    p = Paginator(classes, iPP)
    d = []
    for c in p.get_page(pN).object_list:
        d.append([c.id, c.course.id, c.course.name, c.name, c.course.dept.dept_name, c.course.credit, c.grade_type, c.teacher.name, c.attends, c.amount])
    plist = p.get_elided_page_range(pN, on_each_side=2, on_ends=1)
    pl = json.dumps(list(plist))
    pl = json.loads(pl)
    return JsonResponse({"success": True, "code": 200, "message":"操作成功", "data":{'classes':d, 'plist':pl, 'page':pN, 'total': len(classes)}})


# 查看课程学生API
@login_required
@user_passes_test(user_teacher_and_above)
@require_http_methods(['POST'])
@ensure_csrf_cookie
@transaction.atomic
def get_class_student_api(request):
    c_id = request.POST.get("class_id", "")

    if not c_id:
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})

    c_list = Class.objects.filter(id=c_id).only()
    if len(c_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "班级不存在", "data": ""})
    class_name = "%s-%s" % (c_list[0].course.name, c_list[0].name)

    pN = request.POST.get("page", 1)
    iPP = request.POST.get("itemPerPage", 40)

    student_info_list = StudentCourseInfo.objects.filter(courseClass=c_list[0])
    p = Paginator(student_info_list, iPP)
    d = []
    for s in p.get_page(pN).object_list:
        d.append([s.student.user.uid, s.student.name, s.grade])
    plist = p.get_elided_page_range(pN, on_each_side=2, on_ends=1)
    pl = json.dumps(list(plist))
    pl = json.loads(pl)
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": {'class_name': class_name, 'student':d, 'plist':pl, 'page':pN, 'total': len(student_info_list)}})


# 将学生加入课程API
@login_required
@user_passes_test(user_teacher_and_above)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def assign_student_to_class_api(request):
    operation_list = {"assign", "remove"}

    sid = request.POST.get("student_id", "")
    cid = request.POST.get("class_id", "")
    operation = request.POST.get("operation", "")

    if sid and cid and (operation in operation_list):
        pass
    else:
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})

    student_list = Student.objects.filter(user__uid=sid).only()
    if len(student_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "学生不存在", "data": ""})
    
    class_list = Class.objects.filter(id=cid).only()
    if len(class_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "课程不存在", "data": ""})
    course_class = class_list[0]

    # 教师权限限制
    if request.user.role=="teacher":
        if request.user.teacher != class_list[0].teacher:
            return JsonResponse({"success": False, "code": 400, "message": "权限错误", "data": ""})

    if operation == "assign":
        try:
            record = StudentCourseInfo(student=student_list[0], courseClass=course_class, grade=None, grade_type=course_class.grade_type)
            record.save()
            course_class.attends += 1
            course_class.save()
        except Exception as e:
            return JsonResponse({"success": False, "code": 400, "message": "选课失败", "data": str(e)})
        return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})
    else:
        record_set = StudentCourseInfo.objects.filter(student=student_list[0], courseClass=course_class)
        if len(record_set) == 0:
            return JsonResponse({"success": False, "code": 400, "message": "学生未参加课程", "data": ""})
        record = record_set[0]
        try:
            record.delete()
            course_class.attends -= 1
            course_class.save()
        except Exception as e:
            return JsonResponse({"success": False, "code": 400, "message": "退课失败", "data": str(e)})
        return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})


# 给学生打分API
@login_required
@user_passes_test(user_teacher_and_above)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def score_student_api(request):
    sid = request.POST.get("student_id", "")
    cid = request.POST.get("class_id", "")
    score = request.POST.get("score", "")
    
    if not sid or not cid or not score:
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})
    
    if not score.isnumeric():
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})
    score = int(score)

    if score < 0 or score > 100:
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})

    student_list = Student.objects.filter(user__uid=sid).only()
    if len(student_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "学生不存在", "data": ""})
    
    class_list = Class.objects.filter(id=cid).only()
    if len(class_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "课程不存在", "data": ""})
    
    # 教师权限限制
    if request.user.role=="teacher":
        if request.user.teacher != class_list[0].teacher:
            return JsonResponse({"success": False, "code": 400, "message": "权限错误", "data": ""})

    record_list = StudentCourseInfo.objects.filter(courseClass=class_list[0]).filter(student=student_list[0])
    if len(record_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "学生未参加课程", "data": ""})

    try:
        record = record_list[0]
        record.grade = score
        record.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "给分失败", "data": str(e)})
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
    c_schedule = request.POST.get("course_schedule", "")

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


# 修改课程API
@login_required
@user_passes_test(user_mgmtable)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def mod_course_api(request):
    c_id = request.POST.get("course_id", "")
    c_name = request.POST.get("course_name", "")
    c_description = request.POST.get("course_description", "")
    c_credit = request.POST.get("course_credit", "")
    c_dept = request.POST.get("course_dept", "")
    c_schedule = request.POST.get("course_schedule", "")

    course_set = Course.objects.filter(id=c_id)
    if len(course_set) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "课程ID不存在", "data": ""})
    course = course_set[0]

    if request.user.role == 'dept':
        # 若为院系用户且课程院系不对应
        if request.uesr.department != course.dept:
            return JsonResponse({"success": False, "code": 400, "message": "用户权限错误", "data": ""})
        c_dept = request.user.dept
    else:
        dept_list = Department.objects.filter(dept_no=c_dept)
        if len(dept_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message":"院系ID不存在", "data":""})
        c_dept = dept_list[0]

    try:
        course.name=c_name
        if c_description:
            course.description=c_description
        course.credit=c_credit
        if c_dept:
            course.dept=c_dept
        course.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "修改失败", "data": str(e)})
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
            return JsonResponse({"success": False, "code": 400, "message":"权限错误", "data":""})
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
    c_id = request.POST.get("class_id", "")
    c_name = request.POST.get("class_name", "")
    c_teacher_uid = request.POST.get("class_teacher_uid", "")
    c_amount = request.POST.get("class_amount", "")
    c_grade_type = request.POST.get("class_grade_type", "")

    if c_id and c_name and c_amount and c_grade_type in ('PF', 'SC', '13'):
        pass
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})
    
    class_list = Class.objects.filter(id=c_id).only()
    if len(class_list) == 0:
        return JsonResponse({"success": False, "code": 400, "message":"课程不存在", "data":""})
    courseClass = class_list[0]

    # 若为院系用户且课程院系不对应
    if not request.user.is_superuser:
        if request.user.department != course_list[0].dept:
            return JsonResponse({"success": False, "code": 400, "message":"权限错误", "data":""})
    if c_teacher_uid:
        teacher_list = Teacher.objects.filter(user__uid=c_teacher_uid).only()
        if len(teacher_list) == 0:
            return JsonResponse({"success": False, "code": 400, "message":"教师不存在", "data":""})

    try:
        courseClass.name=c_name
        if c_teacher_uid:
            courseClass.teacher=teacher_list[0]
        courseClass.amount=c_amount
        courseClass.grade_type=c_grade_type
        courseClass.save()
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

    c_id = request.POST.get("course_id", "")
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
    if operation == "del_course":
        if request.user.role == "dept" and request.user.department != c.dept:
            return JsonResponse({"success": False, "code": 400, "message": "权限错误", "data": ""})
    elif operation == "del_class":
        if request.user.role == "dept" and request.user.department != c.course.dept:
            return JsonResponse({"success": False, "code": 400, "message": "权限错误", "data": ""})
        
    try:
        c.delete()
    except:
        return JsonResponse({"success": False, "code": 400, "message":"删除失败", "data":""})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})

# TODO
# 设置课程Schedule API
@login_required
@user_passes_test(user_mgmtable)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def add_schedule_api(request):
    c_id = request.POST.get("class_id", "")
    c_schedule = request.POST.get("course_schedule", "")

    sch_list = None
    try:
        sch_list = json.loads(c_schedule)
        for sch in sch_list:
            if "weekday" in sch.keys() and "start" in sch.keys() and "end" in sch.keys() and "classroom" in sch.keys() and "interval" in sch.keys():
                sch["weekday"] = int(sch["weekday"])
                sch["start"] = datetime.datetime.strptime(sch["start"], '%H:%M')
                sch["end"] = datetime.datetime.strptime(sch["end"], '%H:%M')
                sch["interval"] = int(sch["interval"])
            else:
                raise ValueError("Format error: %s" % str(sch))
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "读取列表失败", "data": str(e)})

    class_set = Class.objects.filter(id=c_id)
    if len(course_set) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "班级ID不存在", "data": ""})
    courseClass = class_set[0]

    # 若为院系用户且课程院系不对应
    if not request.user.is_superuser:
        if request.user.department != course.dept:
            return JsonResponse({"success": False, "code": 400, "message":"权限错误", "data":""})

    try:
        schedule_list = []
        for sch in sch_list:
            s = Schedule(courseClass=courseClass, start=sch["start"], end=sch["end"], weekday=sch["weekday"], week_interval=sch["interval"], location=sch["classroom"])
            schedule_list.append(s)
        for s in schedule_list:
            s.save()
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

# 正在选课学期名称及id
def eelecting_semesters_api(request):
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": {'semesters': get_now_elect_semester()}})