from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse


#current user model
User = get_user_model()

#Shows login form
def login_view(request):
	return render(request,'login.html')

#Login button callback
def validate_login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request,username=username,password=password)
		response = {
			'username_invalid':not(User.objects.filter(username=username).exists()),
			'password_invalid':(user is None)
		}		
		if user is not None:
			login(request,user)
		return JsonResponse(response)

def login_action(request):
	user = request.user
	if user.role == 'student':
		return redirect('/student/')
	elif user.role == 'teacher':
		return redirect('/teacher/')


#Sign up page / Sign up button callback
def signup_view(request):
	return render(request, 'signup.html')

def validate_user(request):
	''' Validates new users '''
	print(request.POST)
	username = request.POST['username']
	password = request.POST['password']
	pass_conf = request.POST['pass_conf']
	usertype = request.POST['usertype']
	fio = request.POST['fio']
	print(password,pass_conf)
	response = {
		'username_is_taken':User.objects.filter(username=username).exists(),
		'password_is_small':(len(password)<=6),
		'password_mismatch':(password!=pass_conf),
		'fio_is_empty':not(bool(fio))
	}
	if not any(response.values()):
		user = User.objects.create_user(username=username,password=password,role=usertype,fio=fio)
		print(User.objects.filter(username=username).exists())
	return JsonResponse(response)


def logout_action(request):
	logout(request)
	return redirect('login')
