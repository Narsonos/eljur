from django.shortcuts import render,redirect
from login.decorators import role_only
from django.contrib.auth import get_user_model
from teachers.models import Mark, StudentsToTeachers, Subject
import datetime



@role_only('student')
def dashboard(request):
	current_user = request.user #student
	print(current_user)
	#fetching date
	start_date = request.POST.get('given_date', default=None)


	#figuring out weekdays (the same as in teachers view)
	today = datetime.date.today()
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


	#marks for the subject
	relations = list(StudentsToTeachers.objects.filter(student=current_user))
	marks = [[Mark.objects.filter(subject=relation.subject, student=relation.student, date=date).first() for date in actual_dates] for relation in relations]
	print(marks)
	#forming table object
	table = zip(relations,marks)
	return render(request,'stud_dash.html',{'dates_and_weekdays':dates_and_weekdays,'fulldates': full_dates, 'table':table, 'selected_date':selected_date})

@role_only('student')
def mystats(request):
	current_user = request.user

	relations = StudentsToTeachers.objects.filter(student=current_user).all()
	print(relations)
	table = []
	for relation in relations:
		student = relation.student
		subject = relation.subject
		total = Mark.objects.filter(subject=subject,student=student).count()
		if total > 0:
			N_attended = Mark.objects.filter(subject=subject,student=student).exclude(value__in=['Н','Б']).count()
			N_ill = Mark.objects.filter(subject=subject,student=student, value__in=['Б']).count()
			
			numeric_marks = Mark.objects.filter(subject=subject,student=student, value__in=['5','4','3','2']).values('value')
			numeric_marks = [int(mark.get('value')) for mark in numeric_marks]

			percent_attended = round(N_attended / total,2)*100
			percent_ill = round(N_ill / total,2)*100

			if len(numeric_marks)>0:
				average_score = round(sum(numeric_marks)/len(numeric_marks),2)
			else:
				average_score = '-'

			print(N_attended)
			print(N_ill)
			print(numeric_marks)
			row = [subject.name,relation.teacher.fio,percent_attended,percent_ill,average_score]
		else:
			row = [subject.name,relation.teacher.fio,'-','-','-']

		table.append(row)
		
	return render(request, 'stud_stats.html',{'table':table})