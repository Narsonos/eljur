from django.urls import path
from .views import login_action,login_view,validate_user,signup_view,validate_login,logout_action

urlpatterns = [
	path('login/',login_view,name='login'),
	path('logout/',logout_action,name='logout'),
	path('sign_up/',signup_view, name='signup'),
	path('validate_user/', validate_user,name='validate_user'),
	path('validate_login/',validate_login,name='validate_login'),
	path('login_action/',login_action,name='login_action')
]