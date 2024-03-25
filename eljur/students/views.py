from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from login.decorators import role_only

# Create your views here.
@role_only('student')
def dashboard(request):
	return render(request,'stud_dash.html')