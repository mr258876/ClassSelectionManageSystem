from django.db import models

def current_year():
    # refer: https://stackoverflow.com/questions/49051017/year-field-in-django/49051348
    return datetime.date.today().year

class Semester(models.Model):
    semester_name = models.CharField(null=True, max_length=20, verbose_name='学期名称')
    semester_year = models.PositiveSmallIntegerField(null=True, verbose_name='学年')
    semester_no = models.PositiveSmallIntegerField(null=True, verbose_name='学期编号')
    start_time = models.DateField(verbose_name='学期开始日期')
    end_time = models.DateField(verbose_name='学期结束日期')
    select_start = models.DateTimeField(verbose_name='选课开始时间')
    select_end = models.DateTimeField(verbose_name='选课结束时间')