from django.urls import path
from .views import dashboard,mystats

urlpatterns = [
	path('student/',dashboard,name='student_dashboard'),
	path('student/my_stats',mystats,name='student_mystats')
]