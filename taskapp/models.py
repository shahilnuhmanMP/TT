#taskappp/models.py
from calendar import day_name
from datetime import timedelta, datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.username

class Child(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    dob = models.DateField()  # Change age to dob (date of birth)
    interests = models.CharField(max_length=255, default='none')  # A single interest as a string
    color_code = models.CharField(max_length=50 , default='#FFFFFF')
    def __str__(self):
        return self.name

class TrustedPerson(models.Model):
    user = models.ForeignKey(get_user_model(),blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=100)
    phone_country_code = models.CharField(max_length=5, blank=True, null=True)
    phone_number = models.CharField(max_length=15)



    def __str__(self):
        return self.name

class Occurrence(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    occurrence_date = models.DateField()
class Event(models.Model):
    summary = models.CharField(max_length=255)
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField(default=timezone.now)
    repeat = models.CharField(max_length=20, choices=[
        ('none', 'Do Not Repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ])
    custom_repeat_days = models.JSONField(null=True, blank=True)
    recurrence_end_option = models.CharField(max_length=20, null=True, blank=True)
    # recurrence_end_value = models.CharField(max_length=255, null=True, blank=True)
    recurrence_end_date = models.DateField(null=True, blank=True)
    recurrence_occurrences = models.IntegerField(null=True, blank=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    trusted_person = models.ForeignKey(TrustedPerson, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fee_date = models.CharField(max_length=20, choices=[('each_event', 'Each Event'), ('monthly', 'Monthly')],
                                default='each_event')
    start_datetime_allday = models.JSONField(null=True, blank=True)
    end_datetime_allday = models.JSONField(null=True, blank=True)
    event_cancelled_dates = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.summary


class Attendance(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attended_dates = models.JSONField(default=list,null=True, blank=True)
    absent_dates = models.JSONField(default=list,null=True, blank=True)
    selected_option =models.CharField(max_length=255, null= True, blank=True)




# models.py
from django.db import models

class Class(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='class_images/', blank=True)  # Add this line for image upload

    def __str__(self):
        return self.title







#23may


class FeePayment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    payment_entries = models.JSONField(default=list)  # Store payment entries as a list of dictionaries
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


class Contacts(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together =('user','name')