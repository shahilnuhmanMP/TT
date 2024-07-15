import json
from datetime import datetime
from django.shortcuts import render
from calendar import day_name
from datetime import timedelta, datetime
from decimal import Decimal
from dateutil import rrule
from taskapp.models import Event, Attendance
from calendar import day_name

# taskapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils import timezone
from .forms import SignUpForm, TrustedPersonForm
from .forms import LoginForm, ProfileForm
from .models import Child, TrustedPerson, Class
from django.contrib.auth.models import User
from django.contrib import messages


def header(request):
    user_children = Child.objects.filter(user=request.user)
    return render(request, 'header.html', {'user_children': user_children})


def home(request):
    if request.user.is_authenticated:

        user_children = Child.objects.filter(user=request.user)
        providers = Class.objects.all()
        now = datetime.now()
        # print("current time",now)

    else:
        user_children = None
        providers = None
        now = datetime.now()
        # Or any other default value you prefer when the user is not authenticated

    return render(request, 'base.html', {'user_children': user_children, 'providers': providers, 'now': now})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = authenticate(request, username=username, password=password)
            login(request, user)

            #            print(f"Username: {username}")
            #           print(f"User ID: {user.id}")
            return redirect('home')  # Update 'home' with the name of your home view
        else:
            #          print("Form is not valid. Errors:", form.errors)

            return render(request, 'signup.html', {'form': form, 'error_message': form.errors})
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        form.user = request.user
        if form.is_valid():
            form.save()
            current_password = form.cleaned_data.get('current_password')
            new_password = form.cleaned_data.get('new_password1')

            if current_password and new_password:
                # Change password only if both current and new passwords are provided
                request.user.set_password(new_password)
                request.user.save()
                # user = authenticate(request, username=request.user.username, password=new_password)
                # login(request, user)
                messages.success(request, 'Password changed successfully')
                update_session_auth_hash(request, request.user)

            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
        form.user = request.user
    return render(request, 'profile.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Update 'home' with the name of your home view
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


# @login_required
# def profile(request):
#     user_children = Child.objects.filter(user=request.user)
#     return render(request, 'header.html', {'user_children': user_children})

def logout_view(request):
    logout(request)
    return redirect('home')


def manage_children_view(request):
    user_children = Child.objects.filter(user=request.user)  # Assuming user is associated with Child model
    trusted_people = TrustedPerson.objects.filter(user=request.user)
    return render(request, 'manage_children.html', {'user_children': user_children, 'trusted_people': trusted_people})


import random
from django.shortcuts import render, redirect
from .models import Child

# def generate_unique_color(user_id):
#     while True:
#         # Generate random transparent color code
#         color_code = f"rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.5)"
#
#         # Check if the color code is already used by other children of the same user
#         if not Child.objects.filter(user_id=user_id, color_code=color_code).exists():
#             return color_code

from django.http import JsonResponse


@login_required
def add_child(request):
    existing_child_names = Child.objects.filter(user=request.user).values_list('name', flat=True)
    if request.method == 'POST':
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        interests = request.POST.getlist('interests')
        color_code = request.POST.get('color_code')

        if name in existing_child_names:
            messages.error(request, 'A child with this name already exists.')
            return render(request, 'add_child.html')

        # Perform your own validation if needed

        child = Child.objects.create(
            name=name,
            gender=gender,
            dob=dob,
            interests=interests,
            color_code=color_code,
            user=request.user
        )

        #        print(f"Child added for user {request.user}: {child.name}")

        return redirect('manage_children')  # Redirect to the profile view after adding a child
    else:
        # Handle GET request
        return render(request, 'add_child.html')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Child


@csrf_exempt
@login_required()
def get_child_color(request):
    if request.method == 'POST':
        child_name = request.POST.get('child_name')
        user = request.user
        try:

            child = Child.objects.get(name=child_name, user=user)
            color_code = child.color_code
            return JsonResponse({'color_code': color_code})
        except Child.DoesNotExist:
            return JsonResponse({'error': 'Child not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def add_trusted_person(request):
    if request.method == 'POST':
        form = TrustedPersonForm(request.POST)
        if form.is_valid():
            trusted_person = form.save(commit=False)
            trusted_person.user = request.user
            trusted_person.save()
            return redirect('manage_children')  # Redirect to the manage_children page after adding a trusted person
    else:
        form = TrustedPersonForm(initial={'phone_country_code': '+91'})
        # form = TrustedPersonForm()

    return render(request, 'add_trusted_person.html', {'form': form})


def calendar_view(request):
    user_children = Child.objects.filter(user=request.user)
    trusted_people = TrustedPerson.objects.filter(user=request.user)
    events = Event.objects.filter(child__in=user_children)
    return render(request, 'calendar.html',
                  {'user_children': user_children, 'trusted_people': trusted_people, 'events': events})


from django.shortcuts import render, redirect
from .models import Event
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def generate_occurrence_dates(event_ch, event_sum, event_id, start_datetime, end_datetime, repeat, custom_repeat_days,
                              recurrence_end_option, recurrence_end_value):
    occurrence_dates = []

    current_date = start_datetime
    #  print("b4first",event_id)
    end_date = recurrence_end_value if recurrence_end_option == 'afterDate' else None

    # print("first",event_id,"end_date",end_date)
    # print(current_date.date())
    occurrences_remaining = recurrence_end_value if recurrence_end_option == 'afterOccurrences' else float('inf')
    #   print("sec", event_id,"end_rem", occurrences_remaining)

    while (end_date is None or current_date.date() <= end_date) and occurrences_remaining > 0:
        if current_date.date() < datetime(2024, 3, 30).date():
            print("iteration currentdate", current_date.date(), "end_date", end_date, occurrences_remaining)
        if repeat == 'daily':
            add_recurring_event(repeat, occurrence_dates, current_date, start_datetime, end_datetime)
            occurrences_remaining -= 1
            current_date += timedelta(days=1)
        elif repeat == 'weekly':
            #        print("argument", repeat, occurrence_dates, current_date, start_datetime, end_datetime)
            add_recurring_event(repeat, occurrence_dates, current_date, start_datetime, end_datetime)
            occurrences_remaining -= 1
            current_date = current_date + timedelta(weeks=1)
        elif repeat == 'monthly':
            add_recurring_event(repeat, occurrence_dates, current_date, start_datetime, end_datetime)
            occurrences_remaining -= 1
            current_date = add_month(current_date)
        elif repeat == 'custom':
            #       print("cameeeeee heerreeee",custom_repeat_days,day_name[current_date.weekday()])
            if custom_repeat_days != 'none' and day_name[current_date.weekday()] in custom_repeat_days:
                #          print("cameeeeeeeeeeeeeeee")
                add_recurring_event(repeat, occurrence_dates, current_date, start_datetime, end_datetime)
                occurrences_remaining -= 1
            current_date += timedelta(days=1)
    #     print("ender")

    return occurrence_dates


def add_recurring_event(repeat, recurringEvents, currentDate, start, end):
    # print(event_id)
    recurringEvents.append({
        'start': currentDate,
        'end': currentDate + (end - start),  # Capture the end date time as well
        # 'title': event.summary,
        # 'allDay': False,
        # 'child':event.child,
    })


def add_month(date):
    if date.month == 12:
        return datetime(year=date.year + 1, month=1, day=date.day, hour=date.hour, minute=date.minute)
    else:
        return datetime(year=date.year, month=date.month + 1, day=date.day, hour=date.hour, minute=date.minute)


@csrf_exempt
@login_required
def save_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        summary = data.get('summary')
        start_datetime = data.get('startDateTime')
        end_datetime = data.get('endDateTime')
        repeat = data.get('repeat')
        custom_repeat_days = data.get('customRepeatDays', [])

        recurrence_end_option = data.get('recurrenceEndOption')
        recurrence_end_date = data.get('recurrenceEndDate')
        recurrence_occurrences = data.get('recurrenceOccurrences')
        fee_amount = Decimal(data.get('fee_amount'))
        fee_date = data.get('fee_date')

        child_id = data.get('childId')
        trusted_person_id = data.get('trustedPersonId')
        # print("ttidtype", type(trusted_person_id))

        user = request.user
        if trusted_person_id != "0":
            # If a trusted person is selected, use it
            trusted_person = trusted_person_id
        else:
            # If no trusted person is selected, use the logged-in user
            trusted_person = None

        event = Event(
            summary=summary,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            repeat=repeat,
            custom_repeat_days=custom_repeat_days,
            recurrence_end_option=recurrence_end_option,
            recurrence_end_date=recurrence_end_date,
            recurrence_occurrences=recurrence_occurrences,
            fee_amount=fee_amount,  # Add fee_amount field
            fee_date=fee_date,
            child_id=child_id,
            trusted_person_id=trusted_person,
            user=user
        )
        event.save()
        event_id = event.id
        generate_and_save_occurrences(event_id)

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})


def generate_and_save_occurrences(event_id):
    event = Event.objects.get(id=event_id)
    # print("basueventeventevent",event)
    event_sum = event.summary

    # print("summmmmmaaarryyy",event_sum)
    event_ch = event.child
    event_id = event.id
    print(event_id)
    start_datetime = event.start_datetime
    # print("Before conversion:", start_datetime)  # Add this line to print the original value

    if isinstance(start_datetime, str):
        try:
            start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
            start_datetime = timezone.make_aware(start_datetime, timezone.get_current_timezone())
        except ValueError as e:
            print("Conversion error:", e)

    # print("After conversion:", start_datetime.strftime('%Y-%m-%d %H:%M:%S%z'))

    # print("mmmmmmmm",output_string)
    end_datetime = event.end_datetime
    if isinstance(end_datetime, str):
        try:
            end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M')
            end_datetime = timezone.make_aware(end_datetime, timezone.get_current_timezone())
        except ValueError as e:
            print("Conversion error:", e)
    # print("coded",end_datetime)

    repeat = event.repeat
    custom_repeat_days = event.custom_repeat_days
    recurrence_end_option = event.recurrence_end_option
    recurrence_end_date = event.recurrence_end_date
    recurrence_occurrences = event.recurrence_occurrences
    # print("event_ch",event_ch,"event_sum",event_sum,"event_id",event_id,"start_datetime",start_datetime,"end_datetime",end_datetime,"repeat",repeat,"custom_repeat_days",custom_repeat_days,"recurrence_end_option",recurrence_end_option,"recurrence_end_date",recurrence_end_date,"recurrence_occurrences",recurrence_occurrences)
    if repeat == 'custom':

        if recurrence_end_option == 'afterDate':
            occurrence_dates = generate_occurrence_dates(event_ch, event_sum, event_id, start_datetime, end_datetime,
                                                         repeat, custom_repeat_days, recurrence_end_option,
                                                         recurrence_end_date)
        else:
            occurrence_dates = generate_occurrence_dates(event_ch, event_sum, event_id, start_datetime, end_datetime,
                                                         repeat, custom_repeat_days,
                                                         recurrence_end_option, recurrence_occurrences)
    else:
        #   print("eventtttttt", event_id)

        custom_repeat_days = 'none'
        if recurrence_end_option == 'afterDate':
            occurrence_dates = generate_occurrence_dates(event_ch, event_sum, event_id, start_datetime, end_datetime,
                                                         repeat, custom_repeat_days,
                                                         recurrence_end_option, recurrence_end_date)
        else:
            occurrence_dates = generate_occurrence_dates(event_ch, event_sum, event_id, start_datetime, end_datetime,
                                                         repeat, custom_repeat_days,
                                                         recurrence_end_option, recurrence_occurrences)
    # print("After calling generate_occurrence_dates")
    # print("occ", occurrence_dates)
    data = occurrence_dates
    start_list = [entry['start'] for entry in data]
    end_list = [entry['end'] for entry in data]
    start = []
    end = []
    sl = []

    for i in start_list:
        formatted_datetime = i.strftime('%Y-%m-%d')[:]
        start.append(formatted_datetime)
    for i in end_list:
        formatted_datetime = i.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        end.append(formatted_datetime)

    event.start_datetime_allday = start
    event.end_datetime_allday = end
    event.save()


# print(type( event.start_datetime_allday))


# views.py in your app
from rest_framework import generics
from .models import Event
from .serializers import EventSerializer
from rest_framework.permissions import IsAuthenticated


class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]


from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime


def view_events_by_child_and_date(request):
    if request.method == 'POST':
        child_id = request.POST.get('child_id')
        selected_date_str = request.POST.get('selected_date')

        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid date format'})

        child_events = Event.objects.filter(child_id=child_id)
        events_on_selected_day = []

        for event in child_events:
            if event.start_datetime_allday and selected_date_str in event.start_datetime_allday:
                events_on_selected_day.append({
                    'id': event.id,
                    'summary': event.summary,
                    'start_datetime': event.start_datetime.strftime('%Y-%m-%d %H:%M:%S%z'),
                    'end_datetime': event.end_datetime.strftime('%Y-%m-%d %H:%M:%S%z'),
                    'repeat': event.repeat,
                    'custom_repeat_days': event.custom_repeat_days,
                    'recurrence_end_option': event.recurrence_end_option,
                    'recurrence_end_date': event.recurrence_end_date,
                    'recurrence_occurrences': event.recurrence_occurrences,
                })

        attendance_data = list(Attendance.objects.filter(child_id=child_id).values())

        return JsonResponse({'status': 'success', 'events': events_on_selected_day, 'attendanceData': attendance_data})

    # If not a POST request, render a page to select child and date
    user_children = Child.objects.filter(user=request.user)
    return render(request, 'select_child_and_date.html', {'user_children': user_children})


@csrf_exempt  # Exempting CSRF for simplicity; consider using CSRF in production
@login_required  # Ensure the user is logged in
def submit_attendance(request):
    try:
        if request.method == 'POST':
            child_id = request.POST.get('child_id')
            event_id = request.POST.get('event_id')
            selected_option = request.POST.get('selected_option')
            selected_date_str = request.POST.get('selected_date')
            #        print(
            #           f"child_id: {child_id}, event_id: {event_id}, selected_option: {selected_option}, selected_date_str: {selected_date_str}")

            # Get or create the Attendance object
            attendance, created = Attendance.objects.get_or_create(
                user=request.user,
                child_id=child_id,
                event_id=event_id,
            )

            # Remove the selected date from attended_dates or absent_dates if it already exists

            if selected_date_str in attendance.attended_dates:
                #          print("yes its there in attended")
                attendance.attended_dates.remove(selected_date_str)

            elif selected_date_str in attendance.absent_dates:
                #         print("yes its there in absent")
                attendance.absent_dates.remove(selected_date_str)

            # Update attended/absent dates and selected_option
            if selected_option == 'attended':
                #        print("came here attended save")
                attendance.attended_dates.append(selected_date_str)
            elif selected_option == 'absent':
                #       print("came here absent save")
                attendance.absent_dates.append(selected_date_str)

            attendance.selected_option = selected_option
            attendance.save()

            return JsonResponse({'status': 'success', 'message': 'Attendance submitted successfully'})
    except Exception as e:
        # print(f"Error in submit_attendance: {str(e)}")

        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


# taskappp/views.py
from django.shortcuts import render
from .models import Child, Event, Attendance
from django.db.models import Count


def child_dashboard(request):
    children = Child.objects.filter(user=request.user)

    if request.method == 'POST':
        child_id = request.POST.get('child_id')
        child = Child.objects.get(id=child_id)

        events = Event.objects.filter(child=child)

        event_data = []
        for event in events:
            attended_dates = Attendance.objects.filter(event=event, child=child).values_list('attended_dates',
                                                                                             flat=True)
            absent_dates = Attendance.objects.filter(event=event, child=child).values_list('absent_dates', flat=True)

            event_data.append({
                'event': event,
                'total_classes': len(event.start_datetime_allday),
                'attended_days': len(attended_dates[0]) if attended_dates else 0,
                'absent_days': len(absent_dates[0]) if absent_dates else 0,
            })

        context = {'child': child, 'children': children, 'event_data': event_data}
        return render(request, 'child_dashboard.html', context)

    return render(request, 'child_dashboard.html', {'children': children})


#
# from django.http import JsonResponse
# from .models import Event
#
# def get_events(request):
#     user_children = Child.objects.filter(user=request.user)
#     child_names = user_children.values_list('name', flat=True)
#
#
#     events = Event.objects.filter(child__name__in=child_names)
#     event_list = []
#
#
#     for event in events:
#         date_object_with_time_cal = []
#         if event.start_datetime_allday:
#             start_datetime = Event.objects.values_list('start_datetime', flat=True).first()
#             date_start_strings = Event.objects.values_list('start_datetime_allday', flat=True).first()
#             for date_start_str in date_start_strings:
#                 date_start_object = datetime.strptime(date_start_str, '%Y-%m-%d')
#                 date_object_with_time = datetime.combine(date_start_object, start_datetime.time())
#                 date_object_with_time_cal.append(date_object_with_time)
#             print("date list", date_object_with_time_cal)
#
#         # If start_datetime_allday is present, use those dates for scheduling
#
#         date_strings = event.end_datetime_allday
#         print("ehnbnbfghfdgssfeses",date_strings)
#
#     if event.end_datetime_allday:
#
#         for date_str,date_start_s in zip(date_strings,date_object_with_time_cal):
#             date_object = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
#             date_start_s_str = date_start_s.strftime('%Y-%m-%d %H:%M:%S.%f')
#             date_object_start=datetime.strptime(date_start_s_str,'%Y-%m-%d %H:%M:%S.%f')
#
#
#             event_list.append({
#                 'title': event.summary,
#                 'start': date_object_start.strftime('%Y-%m-%dT%H:%M:%S'),
#                 'end': date_object.strftime('%Y-%m-%dT%H:%M:%S'),
#                 'child_name': event.child.name if event.child else '',
#             })
#
#         return JsonResponse(event_list, safe=False)
from datetime import datetime
from django.http import JsonResponse
from .models import Child, Event


def get_events(request):
    user_children = Child.objects.filter(user=request.user)
    child_names = user_children.values_list('name', flat=True)

    events = Event.objects.filter(child__name__in=child_names)
    event_list = []

    for event in events:
        date_object_with_time_cal = []

        if event.start_datetime_allday:
            # Use event.start_datetime instead of querying the database again
            start_datetime = event.start_datetime
            date_start_strings = event.start_datetime_allday
            for date_start_str in date_start_strings:
                date_start_object = datetime.strptime(date_start_str, '%Y-%m-%d')
                date_object_with_time = datetime.combine(date_start_object, start_datetime.time())
                date_object_with_time_cal.append(date_object_with_time)
            # print("date list", date_object_with_time_cal)

        # If end_datetime_allday is present, use those dates for scheduling
        if event.end_datetime_allday:
            date_strings = event.end_datetime_allday

            for date_str, date_start_s in zip(date_strings, date_object_with_time_cal):
                date_object = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
                # print("date object",date_object)
                date_start_s_str = date_start_s.strftime('%Y-%m-%d %H:%M:%S.%f')
                date_object_start = datetime.strptime(date_start_s_str, '%Y-%m-%d %H:%M:%S.%f')

                event_list.append({
                    'title': event.summary,
                    'start': date_object_start.strftime('%Y-%m-%dT%H:%M:%S'),
                    'end': date_object.strftime('%Y-%m-%dT%H:%M:%S'),
                    'child_name': event.child.name if event.child else '',
                    'child_id': event.child.id if event.child else '',
                    'event_id': event.id if event.id else '',

                })

    return JsonResponse(event_list, safe=False)


def event_calendar(request):
    events, children = event_list(request)

    return render(request, 'event_calendar.html', {'events': events, 'children': children})


# views.py
from django.shortcuts import render, redirect
from .models import Class
from .forms import ClassForm


def classes_list(request):
    #
    print("request came")
    classes = Class.objects.all()
    #     print("Number of classes:", classes.count())  # Debug statement
    return render(request, 'classes_list.html', {'classes': classes})


def add_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ClassForm()
    return render(request, 'add_class.html', {'form': form})


from django.shortcuts import render
from .models import Event  # Assuming your model name is Event
from datetime import datetime


def event_list(request):
    # Retrieve the currently logged-in user
    current_user = request.user

    # Query all children associated with the current user
    children = Child.objects.filter(user=current_user)

    events = []
    for child in children:
        # Get the current date
        current_date = datetime.now().date()

        # Query events for the current day for the current user's child
        child_events = Event.objects.filter(start_datetime__date=current_date, child=child)

        # Extend the events list with events for the current child
        events.extend(child_events)

    # Pass events data to the template
    # return render(request, 'event_list.html', {'events': events,'children':children})
    return events, children


from rest_framework import generics
from .models import Child, TrustedPerson
from .serializers import ChildSerializer, TrustedPersonSerializer


class ChildListCreateView(generics.ListCreateAPIView):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer


class ChildRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer


class TrustedPersonListCreateView(generics.ListCreateAPIView):
    queryset = TrustedPerson.objects.all()
    serializer_class = TrustedPersonSerializer


class TrustedPersonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrustedPerson.objects.all()
    serializer_class = TrustedPersonSerializer


from .models import Attendance


@login_required()
def get_attendance_data(request):
    current_user = request.user
    event_id = request.GET.get('event_id')
    child_id = request.GET.get('child_id')
    date = request.GET.get('date')
    print(event_id, child_id, date, current_user)

    # Query the Attendance model to get attendance data
    try:

        attendance = Attendance.objects.get(event_id=event_id, child_id=child_id, user=current_user)

        attended = date in attendance.attended_dates
        absent = date in attendance.absent_dates
        return JsonResponse({'attended': attended, 'absent': absent})
    except Attendance.DoesNotExist:
        return JsonResponse({'error': 'Attendance data not found1'}, status=404)