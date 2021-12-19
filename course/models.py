from django.db import models
import datetime
from user.models import Student, Teacher, User
from mgmt.models import Semester
from constants import COURSE_STATUS, COURSE_OPERATION
from django.db.models.deletion import SET_NULL, CASCADE


def current_year():
    # refer: https://stackoverflow.com/questions/49051017/year-field-in-django/49051348
    return datetime.date.today().year


# 院系
class Department(models.Model):
    dept_name = models.CharField(
        max_length=32, null=False, verbose_name="院系名称")
    dept_no = models.CharField(
        max_length=4, verbose_name="院系编号", primary_key=True)
    dept_user = models.OneToOneField(
        User, null=True, verbose_name="院系对应操作用户", on_delete=SET_NULL)
    
    def __str__(self) -> str:
        return '%s, %s' % (self.dept_name, self.dept_no)


# 课程
class Course(models.Model):
    id = models.CharField(max_length=6, primary_key=True, verbose_name='课程编码')
    name = models.CharField(max_length=50, verbose_name="课程名")
    description = models.CharField(
        null=True, max_length=250, verbose_name="课程描述")
    credit = models.IntegerField(verbose_name="学分")
    dept = models.ForeignKey(Department, on_delete=CASCADE, verbose_name='开课院系')
    requirements = models.ManyToManyField('Course', verbose_name='先修课程')

    def __str__(self) -> str:
        return '%s, %s, %s, %s' % (self.id, self.name, self.dept.name, self.credit)


def weekday_choices():
    weekday_str = ['MON', 'TUE', 'WEN', 'THU', 'FRI', 'SAT', 'SUN']
    return [(i+1, weekday_str[i]) for i in range(7)]


# 课程班级
class Class(models.Model):
    name = models.CharField(max_length=32, default='', verbose_name='班级名称')
    course = models.ForeignKey(Course, on_delete=CASCADE, verbose_name='课程')
    teacher = models.ForeignKey(Teacher, on_delete=CASCADE, verbose_name='教师')
    semester = models.ForeignKey(Semester, on_delete=CASCADE, verbose_name='学期')
    amount = models.PositiveIntegerField(null=False, default=0, verbose_name='课程容量')
    attends = models.PositiveIntegerField(null=False, default=0, verbose_name='上课人数')

    GRADE_TYPES = (('PF', '二级制'), ('SC', '百分制'), ('13', '十三级制'))
    grade_type = models.CharField(max_length=2, choices=GRADE_TYPES, default='SC', verbose_name='打分制')

    def __str__(self) -> str:
        schedules = list(self.schedult_set.all())
        return '%s, %s, %s, %s, %s, %s' % (self.id, str(self.course), self.name, self.grade_type, self.teacher.name, str(schedules))


# 课程表
class Schedule(models.Model):
    courseClass = models.ForeignKey(Class, on_delete=CASCADE, verbose_name='课程')
    weekday = models.IntegerField(choices=weekday_choices(), verbose_name="星期")
    start_time = models.TimeField(verbose_name="上课时间")
    end_time = models.TimeField(verbose_name="下课时间")
    location = models.CharField(max_length=100, verbose_name="上课地点")

    intervals = [
        (0, '每周'),
        (1, '单周'),
        (2, '双周')
    ]
    week_interval = models.IntegerField(verbose_name="周间隔", choices=intervals, default=1)

    def __str__(self) -> str:
        return '%s, %s, %s, %s, %s' % (self.week_interval, self.weekday, self.start_time, self.end_time, self.location)


# # 开课申请
# class OpenCourseApplication(models.Model):
#     status = [
#         ('N','待审核'),
#         ('P','通过'),
#         ('F','不通过'),
#     ]

#     teacher = models.ManyToManyField(Teacher, verbose_name='教师')
#     course = models.ManyToManyField(Course, verbose_name='课程')
#     description = models.CharField(null=True, max_length=127, verbose_name= '开课描述')
#     result = models.CharField(null=False, choices=status, max_length=1, default='N', verbose_name='审核状态')


# 学生课程信息
class StudentCourseInfo(models.Model):
    student = models.ForeignKey(Student, on_delete=CASCADE, verbose_name='学生')
    courseClass = models.ForeignKey(Class, on_delete=CASCADE, verbose_name='课程班级')
    grade = models.PositiveIntegerField(null=True, verbose_name='成绩')

    GRADE_TYPES = (('PF', '二级制'), ('SC', '百分制'), ('13', '十三级制'))
    grade_type = models.CharField(max_length=2, choices=GRADE_TYPES, default='SC', verbose_name='打分制')

    def __str__(self) -> str:
        return '%s, %s, %s, %s' % (self.student.user.uid, self.courseClass.course.name, self.grade, self.grade_type)
