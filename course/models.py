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
    dept_name = models.CharField(max_length=32, null=False, verbose_name="院系名称")
    dept_no = models.CharField(max_length=4, verbose_name="院系编号", primary_key=True)
    dept_user = models.OneToOneField(User, null=True, verbose_name="院系对应操作用户", on_delete=SET_NULL)


# 课程
class Course(models.Model):
    id = models.CharField(max_length=6, primary_key=True, verbose_name='课程编码')
    name = models.CharField(max_length=50, verbose_name="课程名")
    description = models.CharField(max_length=250, verbose_name="课程描述")
    credit = models.IntegerField(verbose_name="学分")

    def __str__(self):
        return "%s (%s)" % (self.name, self.teacher.name)


def weekday_choices():
    weekday_str = ['MON', 'TUE', 'WEN', 'THU', 'FRI', 'SAT', 'SUN']
    return [(i+1, weekday_str[i]) for i in range(7)]
    

# 课程表
class Schedule(models.Model):
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


# 课程班级
class Class(models.Model):
    course = models.ForeignKey(Course, on_delete=CASCADE, verbose_name='课程')
    teacher = models.ForeignKey(Teacher, on_delete=CASCADE, verbose_name='教师')
    schedule = models.ForeignKey(Schedule, on_delete=CASCADE, verbose_name='上课时间')


# 学生评分
class StudentCourse(models.Model):
    create_time = models.DateTimeField(auto_now=True)
    with_draw = models.BooleanField(default=False)
    with_draw_time = models.DateTimeField(default=None, null=True)

    scores = models.IntegerField(verbose_name="成绩", null=True)
    comments = models.CharField(max_length=250, verbose_name="老师评价", null=True)

    rates = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    ]

    rating = models.IntegerField(verbose_name="学生评分", choices=rates, null=True, help_text="5分为最满意，最低分是1分")
    assessment = models.CharField(max_length=250, verbose_name="学生评价", null=True)

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


# 开课申请
class OpenCourseApplication(models.Model):
    status = [
        ('N','待审核'),
        ('P','通过'),
        ('F','不通过'),
    ]

    teacher = models.ManyToManyField(Teacher, verbose_name='教师')
    course = models.ManyToManyField(Course, verbose_name='课程')
    description = models.CharField(null=False, max_length=127, verbose_name= '开课描述')
    result = models.CharField(null=False, choices=status, max_length=1, default='N', verbose_name='审核状态')


# 学生课程信息
class StudentCourseInfo(models.Model):
    student = models.ManyToManyField(Student, verbose_name='学生')
    course = models.ManyToManyField(Course, verbose_name='课程')
    semester = models.ManyToManyField(Semester, verbose_name='学期')
    grade = models.PositiveIntegerField(null=True, verbose_name='成绩')


# 课程剩余名额
# 若某课程某学期不开课则无此对象
class CourseSelectInfo(models.Model):
    course = models.ManyToManyField(Course, verbose_name='课程')
    semester = models.ManyToManyField(Semester, verbose_name='学期')
    num_remain = models.PositiveSmallIntegerField(default=0, null=False, verbose_name='剩余名额')