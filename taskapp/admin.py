from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomUser, Child, TrustedPerson, Event, Attendance

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Child)
admin.site.register(TrustedPerson)
admin.site.register(Event)
admin.site.register(Attendance)
