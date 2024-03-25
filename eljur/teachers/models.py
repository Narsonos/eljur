from django.db import models
from django.contrib.auth import get_user_model

#Current user model
User = get_user_model()


class Subject(models.Model):
    name = models.CharField(primary_key=True,max_length=30,null=False)

# Create your models here.
class Mark(models.Model):
    value = models.CharField(max_length=15,blank=False)
    date = models.DateField()
    teacher = models.ForeignKey(User, on_delete=models.SET('Не указан'), related_name='teacher_marks', limit_choices_to={'role':'teacher'})
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_marks', limit_choices_to={'role':'student'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks')

    class Meta:
        unique_together = ('date', 'subject','student')

class StudentsToTeachers(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_assignments', limit_choices_to={'role':'student'})
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_assignments', limit_choices_to={'role':'teacher'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'subject') 