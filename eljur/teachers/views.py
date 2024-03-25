from django.shortcuts import render,redirect
from login.decorators import role_only
from django.contrib.auth import get_user_model
from .models import Mark, StudentsToTeachers, Subject
import datetime


# Create your views here.

#Current user model
User = get_user_model()


########################
#                      #    
#  SECTION: DASHBOARD  #
#                      #
########################

@role_only('teacher')
def dashboard(request):
	current_user = request.user #teacher

	#fetching args
	subject = request.POST.get('given_subject', default=None)
	start_date = request.POST.get('given_date', default=None)

	print(subject,start_date)

	today = datetime.date.today()
	#figuring out weekdays
	if not start_date:
		weekday_offset = today.isoweekday()
		start_date = today - datetime.timedelta(days=weekday_offset-1)
		selected_date = None
	else:
		selected_date = start_date
		start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d').date()
		weekday_offset = start_date.isoweekday()
		start_date = start_date - datetime.timedelta(days=weekday_offset-1)

	actual_dates = [(start_date + datetime.timedelta(days=offset)) for offset in range(7)]
	dates = [(date).strftime('%d/%m') for date in actual_dates]
	full_dates = [date.strftime('%d/%m/%Y') for date in actual_dates]
	weekdays = ['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВС']

	if today >= start_date and today <= start_date + datetime.timedelta(days=7):
		is_today = map(lambda x: dates.index(x)==(weekday_offset-1),dates)
	else:
		is_today = [False for i in range(7)]

	dates_and_weekdays = zip(dates,weekdays,is_today,full_dates)

	#figuring out subjects accessible to the teacher
	my_subjects = StudentsToTeachers.objects.filter(teacher=current_user).values('subject').distinct()
	my_subjects = [x.get('subject') for x in my_subjects]


	#if no subjects -> no students are bound to the teacher
	if not my_subjects:
		return render(request, 'teach_dash.html', {'dates_and_weekdays':dates_and_weekdays, 'table':[], 'my_subjects':[], 'selected_subject': None, 'selected_date':selected_date})

	#if subject wasn't given
	if not subject:
		#getting subject object first
		subject = Subject.objects.filter(name=my_subjects[0]).first()
		selected_subject = None
	else:
		subject = Subject.objects.filter(name=subject).first()
		selected_subject = subject.name
		my_subjects.remove(selected_subject)

	#students for the subject
	relations = list(StudentsToTeachers.objects.filter(teacher=current_user,subject=subject))
	marks = [[Mark.objects.filter(teacher=current_user,subject=subject, student=relation.student, date=date).first() for date in actual_dates] for relation in relations]
	print(marks)
	#forming table object
	table = zip(relations,marks)
	print(selected_subject)
	return render(request,'teach_dash.html',{'dates_and_weekdays':dates_and_weekdays,'fulldates': full_dates, 'table':table, 'my_subjects':my_subjects, 'selected_subject':selected_subject, 'selected_date':selected_date})

@role_only('teacher')
def setmark(request):
	teacher = request.user
	mark = request.POST.get('mark',None)
	fio = request.POST.get('fio',None)
	date = request.POST.get('date',None)
	subject = request.POST.get('subject',None)

	print(
		f"""
		mark = {mark}
		fio = {fio}
		date = {date}
		subject = {subject}
		"""
	)
	#fetching objects based on given data
	if fio and date and subject:
		student = User.objects.filter(fio=fio,role='student').first()
		date = datetime.datetime.strptime(date,'%d/%m/%Y')
		subject = Subject.objects.filter(name=subject).first()

	#setting the mark
	if fio and subject:
		marks = Mark.objects.filter(student=student,subject=subject,teacher=teacher,date=date)
		if mark != '-':
			if marks.first():
				marks.update(value=mark)
			else:
				Mark.objects.create(value=mark,student=student,subject=subject,teacher=teacher,date=date)
		else:
			marks.delete()

	return redirect('teacher_dashboard')


##########################
#                        #    
#  SECTION: MY_STUDENTS  #
#                        #
##########################


@role_only('teacher')
def mystudents(request):
	current_user = request.user 
	all_students = User.objects.filter(role='student')
	my_students = enumerate(StudentsToTeachers.objects.filter(teacher=current_user))
	print(my_students)
	all_subjects = Subject.objects.all()
	return render(request,'teach_stud.html',{'all_subjects':all_subjects,'my_students':my_students, 'all_students':all_students})

@role_only('teacher')
def addstudent(request):
	print(request.POST)
	teacher = request.user
	student_email = request.POST['student_fio'].split(' - ')[0]
	subject = request.POST['subject']

	subject,created = Subject.objects.get_or_create(name=subject)
	student = User.objects.filter(username=student_email).first()

	if student is not None:
		relation = StudentsToTeachers.objects.get_or_create(
			student = student,
			teacher = teacher,
			subject = subject
			)
	return redirect('teacher_mystudents')

@role_only('teacher')
def delstudent(request):
	teacher = request.user
	student_email = request.POST['student']
	subject = request.POST['subject']

	student = User.objects.filter(username=student_email).first()
	subject = Subject.objects.filter(name=subject).first()

	if student is not None and subject is not None:
		StudentsToTeachers.objects.filter(teacher=teacher,student=student,subject=subject).delete()

	print(request.POST)
	return redirect('teacher_mystudents')


##########################
#                        #    
#  SECTION: STATISTICS   #
#                        #
##########################

@role_only('teacher')
def mystats(request):
	current_user = request.user
	subject = request.POST.get('given_subject', default=None)

	#figuring out subjects accessible to the teacher
	my_subjects = StudentsToTeachers.objects.filter(teacher=current_user).values('subject').distinct()
	my_subjects = [x.get('subject') for x in my_subjects]


	#if no subjects -> no students are bound to the teacher -> render empty table
	if not my_subjects:
		return render(request, 'teach_stats.html', {'table':[], 'my_subjects':[], 'selected_subject': None})

	#if subject wasn't given
	if not subject:
		#getting subject object first
		subject = Subject.objects.filter(name=my_subjects[0]).first()
		selected_subject = None
	else:
		subject = Subject.objects.filter(name=subject).first()
		selected_subject = subject.name
		my_subjects.remove(selected_subject)

	relations = StudentsToTeachers.objects.filter(teacher=current_user, subject=subject).all()

	table = []
	for relation in relations:
		student = relation.student
		total = Mark.objects.filter(teacher=current_user,subject=subject,student=student).count()
		if total > 0:
			N_attended = Mark.objects.filter(teacher=current_user,subject=subject,student=student).exclude(value__in=['Н','Б']).count()
			N_ill = Mark.objects.filter(teacher=current_user,subject=subject,student=student, value__in=['Б']).count()
			
			numeric_marks = Mark.objects.filter(teacher=current_user,subject=subject,student=student, value__in=['5','4','3','2']).values('value')
			numeric_marks = [int(mark.get('value')) for mark in numeric_marks]

			percent_attended = round(N_attended / total,2)
			percent_ill = round(N_ill / total,2)

			if len(numeric_marks)>0:
				average_score = round(sum(numeric_marks)/len(numeric_marks),2)
			else:
				average_score = '-'

			print(N_attended)
			print(N_ill)
			print(numeric_marks)
			row = [student.fio,percent_attended,percent_ill,average_score]
		else:
			row = [student.fio,'-','-','-']

		table.append(row)

	return render(request, 'teach_stats.html',{'table':table,'subject':subject,'selected_subject':selected_subject, 'my_subjects':my_subjects})