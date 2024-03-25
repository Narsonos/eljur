from django.urls import path
from .views import dashboard,setmark, mystudents, addstudent,delstudent,mystats

urlpatterns = [
	path('teacher/',dashboard,name='teacher_dashboard'),
	path('teacher/set_mark/',setmark,name='teacher_set_mark'),
	path('teacher/my_students/',mystudents,name='teacher_mystudents'),
	path('teacher/my_students/add_student',addstudent,name='teacher_add_student'),
	path('teacher/my_students/del_student',delstudent,name='teacher_del_student'),
	path('teacher/my_stats',mystats,name='teacher_mystats')
]