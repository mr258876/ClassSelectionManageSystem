from typing import List, Tuple
from .models import Semester
import datetime

def get_current_semester() -> Semester:
    s_list = Semester.objects.filter(start_time__lte=datetime.date.today()).filter(end_time__gte=datetime.date.today())
    if len(s_list) == 0:
        s_list = Semester.objects.filter(start_time__gte=datetime.date.today()).order_by('start_time')
    return s_list[0]

def get_semester_ids() -> List[Tuple[int, str]]:
    result_list = []
    s_list = Semester.objects.all()
    for s in s_list:
        result_list.append((s.id, s.semester_name))
    return result_list

def get_now_elect_semester() -> Semester:
    s_list = Semester.objects.filter(select_start__lte=datetime.datetime.now()).filter(select_end__gte=datetime.datetime.now())
    if len(s_list) == 0:
        return None
    return s_list[0]