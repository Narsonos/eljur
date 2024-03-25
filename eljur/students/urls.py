from django.urls import path
from .views import dashboard

urlpatterns = [
	path('student/',dashboard,name='student_dashboard')
]