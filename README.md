# ClassSelectionManageSystem
Class Selection Manage System, 选课管理系统

Abandoned 项目终止

## Version
#### Python   version: 3.9.0
#### Django   version: 3.2.8
#### Psycopg2 version: 2.9.1

Install requirements:
```txt
pip3 install django==3.2.8
pip3 install psycopg2==2.9.1
```

Database Setup:
```txt
python manage.py makemigrations
python manage.py makemigrations user
python manage.py makemigrations mgmt
python manage.py makemigrations course
python manage.py migrate
```

Create Superuser Account:
```txt
python manage.py createsuperuser
```

## TODO
- student opeartion
- search course


## Problems
#### 1 如何给Class-Based Views 的as_view()生成的view方法里面传参。
比如UpdateTeacherView和UpdateStudentView里面获取不到view方法传入的其他参数
解决方法： 重写get_context_data()， 在里面先写入固定的参数