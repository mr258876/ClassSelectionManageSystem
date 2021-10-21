# ClassSelectionManageSystem
Class Selection Manage System, 选课管理系统

Still in Progress, 正在开发中

## Version
#### Python   version: 3.9.0
#### Django   version: 3.2.8
#### Psycopg2 version: 2.9.1

Install requirements:
```txt
pip3 install django==3.2.8
pip3 install psycopg2==2.9.1
```

Setup:
```txt
python manage.py makemigrations
python manage.py migrate
```

## TODO
- student opeartion
- search course
- form css


## Problems
#### 1 如何给Class-Based Views 的as_view()生成的view方法里面传参。
比如UpdateTeacherView和UpdateStudentView里面获取不到view方法传入的其他参数
解决方法： 重写get_context_data()， 在里面先写入固定的参数