from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)


from django.db import models
from django.contrib.auth.models import User

class StudyPlan(models.Model):
    CLASS_CHOICES = [(str(i), f"Class {i}") for i in range(6, 13)]
    SUBJECT_CHOICES = [
        ('Maths','Maths'), ('Physics','Physics'), ('Chemistry','Chemistry'),
        ('Biology','Biology'), ('English','English'), ('Hindi','Hindi'),
        ('Social Science','Social Science'), ('Economics','Economics'),
        ('History','History'), ('Political Science','Political Science')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=2, choices=CLASS_CHOICES)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    total_days = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class StudyDay(models.Model):
    plan = models.ForeignKey(StudyPlan, related_name="days", on_delete=models.CASCADE)
    day_number = models.PositiveIntegerField()
    topic = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('plan', 'day_number')
        ordering = ['day_number']
        

from django import forms
from .models import StudyDay  # replace with your model

class YourModelForm(forms.ModelForm):
    class Meta:
        model = StudyDay
        fields = '__all__'   # or list specific fields ['name', 'description', ...]
