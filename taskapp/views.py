import json
from datetime import datetime

from django.db.models.fields.json import KeyTextTransform
from silk.profiling.profiler import silk_profile
from django.db.models import Q
from django.shortcuts import render
from calendar import day_name
from datetime import timedelta, datetime
from decimal import Decimal
from dateutil import rrule
from taskapp.models import Event, Attendance, FeePayment
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
def aboutus(request):
    # user_children = Child.objects.filter(user=request.user)
    return render(request, 'about_us.html')





def home(request):
    print('came inside home request')

    user_children = None
    events = None
    providers = None
    now = datetime.now()

    if request.user.is_authenticated:
        user_children = Child.objects.filter(user=request.user)
        events = Event.objects.filter(child__in=user_children).select_related('child')
        providers = Class.objects.all()

    context = {
        'user_children': user_children,
        'providers': providers,
        'now': now,
        'events': events,
    }



    return render(request, 'base.html', context)


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
            #
            #
            #
            #
            #
            #
            #
            #        (f"User ID: {user.id}")
            return redirect('home')  # Update 'home' with the name of your home view
        else:
            #          print("Form is not valid. Errors:", form.errors)

            return render(request, 'signup.html', {'form': form, 'error_message': form.errors})
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def profile(request):
    print('came inside profile request')
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
    print('came inside login view request')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Update 'home' with the name of your home view
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')


def manage_children_view(request):
    print('came inside manage_children_view request')
    user_children = Child.objects.filter(user=request.user)  # Assuming user is associated with Child model
    trusted_people = TrustedPerson.objects.filter(user=request.user)
    return render(request, 'manage_children.html', {'user_children': user_children, 'trusted_people': trusted_people})



@login_required
def add_child(request):
    print('came inside add child request')
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
        return redirect('manage_children')  # Redirect to the profile view after adding a child
    else:
        # Handle GET request
        return render(request, 'add_child.html')

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
@login_required()
def get_child_color(request):
    print('came inside get_child_color request')
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
    print('came inside add trusted per request')
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

# @silk_profile(name='My View Profile')

def calendar_view(request):
    print('came inside calendar_view request')
    user_children = Child.objects.filter(user=request.user)
    trusted_people = TrustedPerson.objects.filter(user=request.user)
    events = Event.objects.filter(child__in=user_children).select_related('child')


    return render(request,'calendar.html',
                  {'user_children': user_children, 'trusted_people': trusted_people, 'events': events})

from django.views.decorators.csrf import csrf_exempt


def generate_occurrence_dates(event_ch, event_sum, event_id, start_datetime, end_datetime, repeat, custom_repeat_days,
                              recurrence_end_option, recurrence_end_value):
    print('came inside generate_occurrence_dates request')
    occurrence_dates = []

    current_date = start_datetime

    end_date = recurrence_end_value if recurrence_end_option == 'afterDate' else None

    occurrences_remaining = recurrence_end_value if recurrence_end_option == 'afterOccurrences' else float('inf')


    while (end_date is None or current_date.date() <= end_date) and occurrences_remaining > 0:

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
    return occurrence_dates


def add_recurring_event(repeat, recurringEvents, currentDate, start, end):
    print('came inside add_recurring_event request')
    # print(event_id)
    recurringEvents.append({
        'start': currentDate,
        'end': currentDate + (end - start),  # Capture the end date time as well

    })


def add_month(date):
    print('came inside add_month request')
    if date.month == 12:
        return datetime(year=date.year + 1, month=1, day=date.day, hour=date.hour, minute=date.minute)
    else:
        return datetime(year=date.year, month=date.month + 1, day=date.day, hour=date.hour, minute=date.minute)

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
@csrf_exempt
@login_required
def save_event(request):
    print('came inside save_event request')
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data,'save event request')

        summary = data.get('summary')
        start_datetime = data.get('startDateTime')

        end_time = data.get('endTime')
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
        start_datetime_obj = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
        end_time_obj = datetime.strptime(end_time, '%H:%M').time()
        end_datetime_obj = datetime.combine(start_datetime_obj.date(), end_time_obj)
        end_datetime_obj = timezone.make_aware(end_datetime_obj, timezone.get_current_timezone())

        event = Event(
            summary=summary,
            start_datetime=start_datetime,

            end_datetime=end_datetime_obj,
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
    print('came inside generate_and_save_occurrences request')
    event = Event.objects.select_related('child').get(id=event_id)
    # print("basueventeventevent",event)
    event_sum = event.summary

    # print("summmmmmaaarryyy",event_sum)
    event_ch = event.child
    event_id = event.id
    # print(event_id)
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





def view_events_by_child_and_date(request):
    print('came inside view_events_by_child_and_date request')
    user = request.user
    if request.method == 'POST':
        child_id = request.POST.get('child_id')
        selected_date_str = request.POST.get('selected_date')

        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid date format'})

        child_events = Event.objects.filter(child_id=child_id,user_id=user)
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
        # print(events_on_selected_day,"evw",'atte',attendance_data)

        return JsonResponse({'status': 'success', 'events': events_on_selected_day, 'attendanceData': attendance_data})

    # If not a POST request, render a page to select child and date
    user_children = Child.objects.filter(user=request.user)
    return render(request, 'select_child_and_date.html', {'user_children': user_children})
@csrf_exempt  # Exempting CSRF for simplicity; consider using CSRF in production
@login_required  # Ensure the user is logged in
def submit_attendance(request):
    print('came inside submit_attendance request')
    try:
        if request.method == 'POST':
            child_id = request.POST.get('child_id')
            event_id = request.POST.get('event_id')
            selected_option = request.POST.get('selected_option')
            selected_date_str = request.POST.get('date')

            # print("data came attendance",child_id,event_id,selected_option,selected_date_str)

            attendance, created = Attendance.objects.get_or_create(
                user=request.user,
                child_id=child_id,
                event_id=event_id,
            )

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

from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)



from django.http import JsonResponse, HttpResponseRedirect


def get_events(request):
    print('came inside get_events request')
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
                    'color':event.child.color_code if event.child else '',

                })

    return JsonResponse(event_list, safe=False)

# @silk_profile(name='event calendar')
def event_calendar(request):
    print('came inside event_calendar request')
    events, children = event_list(request)

    return render(request, 'event_calendar.html', {'events': events, 'children': children})


# views.py
from django.shortcuts import render, redirect
from .models import Class
from .forms import ClassForm


def classes_list(request):
    print('came inside classes_list request')
    #

    classes = Class.objects.all()
    #     print("Number of classes:", classes.count())  # Debug statement
    return render(request, 'classes_list.html', {'classes': classes})


def add_class(request):
    print('came inside add_class request')
    if request.method == 'POST':
        form = ClassForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ClassForm()
    return render(request, 'add_class.html', {'form': form})

def event_list(request):
    print('came inside event_list request')
    # Retrieve the currently logged-in user
    current_user = request.user
    # Query all children associated with the current user
    children = Child.objects.filter(user=current_user)


    events = []
    for child in children:
        # Get the current date
        current_date = datetime.now().date()
        child_events = Event.objects.filter (Q(start_datetime_allday__contains=[str(current_date)]),
            child=child
        )

        events.extend(child_events)

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
    print('came inside get_attendance_data request')
    current_user = request.user
    event_id = request.GET.get('event_id')
    child_id = request.GET.get('child_id')
    date = request.GET.get('date')

    try:

        attendance = Attendance.objects.get(event_id=event_id, child_id=child_id, user=current_user)

        attended = date in attendance.attended_dates
        absent = date in attendance.absent_dates
        return JsonResponse({'attended': attended, 'absent': absent})
    except Attendance.DoesNotExist:
        return JsonResponse({'error': 'Attendance data not found1'}, status=404)


from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def contact_view(request):
    print('came inside contact_view request')
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        company = request.POST.get('company')
        message = request.POST.get('message')

        # Send an email
        send_mail(
            f"New contact form submission from {name}",
            f"Name: {name}\nEmail: {email}\nPhone: {phone}\nCompany: {company}\n\nMessage:\n{message}",
            'email',  # From email
            ['hello@tinytaskers.com'],  # To email
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    return render(request, 'contactform.html')

def contact_success_view(request):
    print('came inside contact_success_view request')
    return render(request,'success.html')



# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# import json
# from datetime import datetime
#
# @login_required
# def fee_payment_view(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#     user = request.user
#
#     fee_payment, created = FeePayment.objects.get_or_create(
#         event=event,
#         user=user,
#         defaults={'payment_entries': []}
#     )
#
#     if request.method == 'POST':
#         paid_amount = request.POST.get('paid_amount')
#         fee_date = request.POST.get('payment_date') if event.fee_date == 'each_event' else request.POST.get(
#             'payment_month')
#
#         # Validate fee_date format and convert to string
#         if event.fee_date == 'each_event':
#             payment_date = datetime.strptime(fee_date, "%Y-%m-%d").date()
#         else:
#             payment_date = datetime.strptime(fee_date, "%Y-%m").date()
#
#         payment_date_str = payment_date.isoformat()  # Convert date to ISO format string
#
#         # Check if payment for the same date already exists
#         if any(entry['payment_date'] == payment_date_str for entry in fee_payment.payment_entries):
#             # Handle the case where the payment date already exists
#             occurrences = event.start_datetime_allday if isinstance(event.start_datetime_allday, list) else json.loads(
#                 event.start_datetime_allday)
#             current_year = datetime.now().year
#             years_range = range(current_year, current_year + 10)  # Adjust range as needed
#
#             return render(request, 'fee_payment.html', {
#                 'event': event,
#                 'occurrences': occurrences,
#                 'years_range': years_range,
#                 'fee_payment': fee_payment,
#                 'error': 'A payment for this date already exists.'
#             })
#
#         # Create new payment entry
#         payment_entry = {
#             'paid_amount': float(paid_amount),
#             'payment_date': payment_date_str
#         }
#
#         fee_payment.payment_entries.append(payment_entry)  # Append new payment entry
#         fee_payment.save()
#
#         return redirect('user_events')
#
#     occurrences = event.start_datetime_allday if isinstance(event.start_datetime_allday, list) else json.loads(
#         event.start_datetime_allday)
#     current_year = datetime.now().year
#     years_range = range(current_year, current_year + 10)  # Adjust range as needed
#
#     # Extract paid dates
#     paid_dates = [entry['payment_date'] for entry in fee_payment.payment_entries]
#
#     # Extract months from occurrences
#     occurrence_dates = [datetime.strptime(date_str, "%Y-%m-%d").date() for date_str in occurrences]
#     occurrence_months = sorted(set(date.strftime("%Y-%m") for date in occurrence_dates))
#
#     # Sort payment entries by payment_date
#     sorted_payment_entries = sorted(fee_payment.payment_entries, key=lambda x: x['payment_date'])
#
#     context = {
#         'event': event,
#         'occurrences': occurrences,
#         'years_range': years_range,  # Pass the range of years to the template
#         'fee_payment': fee_payment,  # Pass fee_payment to the template
#         'paid_dates': paid_dates,  # Pass paid dates to the template
#         'sorted_payment_entries': sorted_payment_entries,  # Pass sorted payment entries to the template
#         'occurrence_months': occurrence_months,  # Pass occurrence months to the template
#     }
#     return render(request, 'fee_payment.html', context)
#
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime

@login_required
def fee_payment_view(request, event_id):
    print('came inside fee_payment_view request')
    event = get_object_or_404(Event, id=event_id)
    user = request.user

    fee_payment, created = FeePayment.objects.get_or_create(
        event=event,
        user=user,
        defaults={'payment_entries': []}
    )

    if request.method == 'POST':
        paid_amount = request.POST.get('paid_amount')
        if event.fee_date == 'each_event':
            fee_date = request.POST.get('payment_date')
        elif event.fee_date == 'monthly':
            fee_date = request.POST.get('payment_month')
        elif event.fee_date == 'Quarterly':
            fee_date = request.POST.getlist('selected_months')  # Expecting a list of 3 months
        # print(fee_date,"came")

        if event.fee_date == 'each_event':
            payment_date = datetime.strptime(fee_date, "%Y-%m-%d").date()
            payment_date_str = payment_date.isoformat()
        elif event.fee_date == 'monthly':
            payment_date = datetime.strptime(fee_date, "%Y-%m").date()
            payment_date_str = payment_date.isoformat()
        elif event.fee_date == 'Quarterly':
            fee_dates_str = request.POST.get('selected_months')
            payment_dates = fee_dates_str.split(', ')
            # print("came inside loop")
            payment_dates = [datetime.strptime(date, "%Y-%m").date() for date in payment_dates]
            # print(payment_dates,'came dates conv')
            payment_date_str = [date.isoformat() for date in payment_dates]
            # print(payment_date_str,'string')
            payment_date_str_len=len(payment_date_str)


        if event.fee_date == 'Quarterly':
            for date in payment_date_str:
                if any(entry['payment_date'] == date for entry in fee_payment.payment_entries):
                    occurrences = event.start_datetime_allday if isinstance(event.start_datetime_allday, list) else json.loads(
                        event.start_datetime_allday)
                    current_year = datetime.now().year
                    years_range = range(current_year, current_year + 10)
                    return render(request, 'fee_payment.html', {
                        'event': event,
                        'occurrences': occurrences,
                        'years_range': years_range,
                        'fee_payment': fee_payment,
                        'error': 'A payment for one of these dates already exists.'
                    })
            for date in payment_date_str:

                payment_entry = {
                    'paid_amount': float(paid_amount) / payment_date_str_len,  # Distribute the amount over 3 months
                    'payment_date': date
                }
                fee_payment.payment_entries.append(payment_entry)
        else:
            if any(entry['payment_date'] == payment_date_str for entry in fee_payment.payment_entries):
                occurrences = event.start_datetime_allday if isinstance(event.start_datetime_allday, list) else json.loads(
                    event.start_datetime_allday)
                current_year = datetime.now().year
                years_range = range(current_year, current_year + 10)
                return render(request, 'fee_payment.html', {
                    'event': event,
                    'occurrences': occurrences,
                    'years_range': years_range,
                    'fee_payment': fee_payment,
                    'error': 'A payment for this date already exists.'
                })

            payment_entry = {
                'paid_amount': float(paid_amount),
                'payment_date': payment_date_str
            }
            fee_payment.payment_entries.append(payment_entry)

        fee_payment.save()
        return redirect('user_events')

    occurrences = event.start_datetime_allday if isinstance(event.start_datetime_allday, list) else json.loads(
        event.start_datetime_allday)
    current_year = datetime.now().year
    years_range = range(current_year, current_year + 10)
    paid_dates = [entry['payment_date'] for entry in fee_payment.payment_entries]
    occurrence_dates = [datetime.strptime(date_str, "%Y-%m-%d").date() for date_str in occurrences]
    occurrence_months = sorted(set(date.strftime("%Y-%m") for date in occurrence_dates))
    sorted_payment_entries = sorted(fee_payment.payment_entries, key=lambda x: x['payment_date'])

    context = {
        'event': event,
        'occurrences': occurrences,
        'years_range': years_range,
        'fee_payment': fee_payment,
        'paid_dates': paid_dates,
        'sorted_payment_entries': sorted_payment_entries,
        'occurrence_months': occurrence_months,
    }
    return render(request, 'fee_payment.html', context)

@login_required
def user_events_view(request):
    print('came inside user_events_view request')
    user = request.user
    events = Event.objects.filter(user=user).select_related('child')
    # print(events,"events my events")


    return render(request, 'user_events.html', {'events': events})


def get_events_for_date(request):
    print('came inside get_events_for_date request')
    user = request.user
    date = request.GET.get('date')
    # print(date,'from request')

    # Fetch events for the specified date
    events = Event.objects.filter(start_datetime_allday__contains=[str(date)],child__user=user)

    event_list = []

    # Iterate over each event
    for event in events:
        fee_payment = FeePayment.objects.filter(event=event, user=request.user).first()
        payment_entries = fee_payment.payment_entries if fee_payment else []
        # Fetch attendance record for the event on the specified date
        # print(event.id,'eventid attendance')
        # print(user.id,'userid attendance')
        attendance_record = Attendance.objects.filter(
            event_id=event.id,
            user_id=user.id,

        ).first()



        # Determine attendance status based on the fetched record
        if attendance_record:
            # print(event.id,'evnt id for the attendance')


            # Check if the selected date is in the attended_dates
            if Attendance.objects.filter(attended_dates__contains=[str(date)],event_id=event.id):
                attendance_status = 'Attended'
            # Check if the selected date is in the absent_dates
            elif Attendance.objects.filter(absent_dates__contains=[str(date)],event_id=event.id):
                attendance_status = 'Absent'
            else:
                attendance_status = 'Not recorded'
        else:
            attendance_status = 'Not recorded'

        # Append event details along with attendance status to the event_list
        event_list.append({
            'id': event.id,
            'title': event.summary,
            'start': event.start_datetime.strftime('%I:%M %p'),  # Format start datetime
            'end': event.end_datetime.strftime('%I:%M %p'),  # Format end datetime
            'child': event.child_id,
            'childname': event.child.name,
            'attendance_status': attendance_status,
            'color':event.child.color_code,
            'payment_entries':payment_entries,
            'fee_date': event.fee_date,
            'fee_amount': event.fee_amount,
            'event_cancelled_dates': event.event_cancelled_dates.split(',') if event.event_cancelled_dates else []
        })

        # print(event_list,"event_list")

    return JsonResponse({'events': event_list})



from django.urls import reverse_lazy, reverse
from django.contrib.auth import views as auth_views
from .forms import PasswordResetForm

class CustomPasswordResetView(auth_views.PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'registration/password_reset_custom.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    html_email_template_name = 'registration/password_reset_email.html'


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import FeePayment, Event, Child, Attendance
from itertools import chain
from datetime import datetime
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# from silk.profiling.profiler import silk_profile
from datetime import datetime
from .models import FeePayment, Event, Child, Attendance
from itertools import chain

@login_required
# @silk_profile(name='My View Profile')
def dashboard_view(request):
    print('came inside dashboard_view request')
    month_names = {
        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
    }
    user = request.user

    # Calculate total spent
    total_spent = sum(entry['paid_amount'] for payment in FeePayment.objects.filter(user=user) for entry in payment.payment_entries)

    # Calculate total classes
    total_classes_count = Event.objects.filter(user=user).count()

    # Calculate spends by event
    event_spends = {}
    for event in Event.objects.filter(user=user):
        event_total = sum(entry['paid_amount'] for payment in FeePayment.objects.filter(event=event) for entry in payment.payment_entries)
        event_spends[event.summary] = event_total

    # Calculate spends by child
    child_spends = {}
    for child in Child.objects.filter(user=user):
        child_total = sum(entry['paid_amount'] for event in Event.objects.filter(child=child) for payment in FeePayment.objects.filter(event=event) for entry in payment.payment_entries)
        child_spends[child.name] = child_total

    # Calculate monthly spends
    monthly_spends = {}
    monthly_event_spends = {}
    monthly_child_spends = {}
    payments = FeePayment.objects.filter(user=user)
    for payment in payments:
        for entry in payment.payment_entries:
            payment_date = datetime.strptime(entry['payment_date'], "%Y-%m-%d")
            month = payment_date.strftime("%B %Y")
            if month not in monthly_spends:
                monthly_spends[month] = 0
                monthly_event_spends[month] = {}
                monthly_child_spends[month] = {}
            monthly_spends[month] += entry['paid_amount']
            event_name = payment.event.summary if payment.event else 'No Event'
            child_name = payment.event.child.name if payment.event and payment.event.child else 'No Child'

            if event_name not in monthly_event_spends[month]:
                monthly_event_spends[month][event_name] = 0
            if child_name not in monthly_child_spends[month]:
                monthly_child_spends[month][child_name] = 0

            monthly_event_spends[month][event_name] += entry['paid_amount']
            monthly_child_spends[month][child_name] += entry['paid_amount']

    # Generate month-year combinations
    current_year = datetime.now().year
    years = range(2024, current_year + 1)  # Adjust start year as needed
    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    month_years = [f"{month} {year}" for year in years for month in months]

    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    selected_month_year = request.POST.get('monthYear')
    child_id = request.POST.get('child_id')
    event_data = []

    if request.method == 'POST' and selected_month_year:
        try:
            selected_month, selected_year = selected_month_year.split()
            selected_month = list(month_names.keys())[list(month_names.values()).index(selected_month)]

            child = Child.objects.get(id=child_id)
            events = Event.objects.filter(child=child)

            for event in events:
                total_classes = [date for date in event.start_datetime_allday if date.startswith(f"{selected_year}-{int(selected_month):02d}")]
                attended_dates_raw = list(chain.from_iterable(Attendance.objects.filter(event=event, child=child).values_list('attended_dates', flat=True)))
                attended_dates = [date for date in attended_dates_raw if date.startswith(f"{selected_year}-{int(selected_month):02d}")]
                absent_dates_raw = list(chain.from_iterable(Attendance.objects.filter(event=event, child=child).values_list('absent_dates', flat=True)))
                absent_dates = [date for date in absent_dates_raw if date.startswith(f"{selected_year}-{int(selected_month):02d}")]

                fee_payments = FeePayment.objects.filter(event=event)

                monthly_total = sum(
                    entry['paid_amount']
                    for payment in fee_payments
                    for entry in payment.payment_entries
                    if entry['payment_date'].startswith(f"{selected_year}-{int(selected_month):02d}")
                )

                event_data.append({
                    'selected_month': month_names[selected_month.zfill(2)],
                    'child': child,
                    'event': event,
                    'total_classes': len(total_classes),
                    'attended_days': len(attended_dates),
                    'absent_days': len(absent_dates),
                    'event_dia_total': monthly_total,
                })
        except Child.DoesNotExist:
            context = {
                'children': Child.objects.filter(user=user),
                'months': months,
                'years': years,
                'month_years': month_years,
                'total_spent': total_spent,
                'total_classes_count': total_classes_count,
                'event_spends': event_spends,
                'child_spends': child_spends,
                'monthly_spends': monthly_spends,
                'monthly_event_spends': monthly_event_spends,
                'monthly_child_spends': monthly_child_spends,
                'error': 'Child does not exist.',
                'event_data': event_data,
            }
            return render(request, 'dashboard.html', context)

    if request.method == 'POST' and not event_data:
        try:
            child = Child.objects.get(id=child_id)
        except Child.DoesNotExist:
            child = None
    else:
        child = Child.objects.filter(user=user).first()

    if child and not event_data:
        events = Event.objects.filter(child=child)
        child_spends_event = {}
        for event in events:
            attended_dates_raw = list(chain.from_iterable(Attendance.objects.filter(event=event, child=child).values_list('attended_dates', flat=True)))
            absent_dates_raw = list(chain.from_iterable(Attendance.objects.filter(event=event, child=child).values_list('absent_dates', flat=True)))

            fee_payments = FeePayment.objects.filter(event=event)
            event_dia_total = sum(entry['paid_amount'] for payment in fee_payments for entry in payment.payment_entries)
            child_spends_event[event.summary] = event_dia_total

            event_data.append({
                'event': event,
                'child': child,
                'total_classes': len(event.start_datetime_allday),
                'attended_days': len(attended_dates_raw),
                'absent_days': len(absent_dates_raw),
                'event_dia_total': child_spends_event[event.summary],
            })

    context = {
        'total_spent': total_spent,
        'total_classes_count': total_classes_count,
        'event_spends': event_spends,
        'child_spends': child_spends,
        'monthly_spends': monthly_spends,
        'monthly_event_spends': monthly_event_spends,
        'monthly_child_spends': monthly_child_spends,
        'children': Child.objects.filter(user=user),
        'months': months,
        'years': years,
        'month_years': month_years,
        'child': child,
        'event_data': event_data,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'selected_month_year': selected_month_year,
    }

    return render(request, 'dashboard.html', context)








@login_required
def child_activities_view(request, child_id):
    print('came inside child_activities_view request')
    child = Child.objects.get(id=child_id)
    attendances = Attendance.objects.filter(child=child)
    fee_payments = FeePayment.objects.filter(event__in=[a.event for a in attendances])

    total_spent = 0
    for payment in fee_payments:
        for entry in payment.payment_entries:
            total_spent += entry.get('paid_amount', 0)

    total_attended = sum(len(a.attended_dates) for a in attendances)
    total_absent = sum(len(a.absent_dates) for a in attendances)

    context = {
        'child': child,
        'total_spent': total_spent,
        'total_attended': total_attended,
        'total_absent': total_absent,
        'attendances': attendances,
        'fee_payments': fee_payments,
    }

    return render(request, 'child_activities.html', context)









from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from decimal import Decimal

@csrf_exempt
@login_required
def update_event(request, event_id):
    print('came inside update_event request')
    if request.method == 'PUT':
        data = json.loads(request.body)
        event = Event.objects.get(id=event_id)

        event.summary = data.get('summary', event.summary)
        event.start_datetime = data.get('startDateTime', event.start_datetime)
        event.end_datetime = data.get('endTime', event.end_datetime)
        event.repeat = data.get('repeat', event.repeat)
        event.custom_repeat_days = data.get('customRepeatDays', event.custom_repeat_days)
        event.recurrence_end_option = data.get('recurrenceEndOption', event.recurrence_end_option)
        event.recurrence_end_date = data.get('recurrenceEndDate', event.recurrence_end_date)
        event.recurrence_occurrences = data.get('recurrenceOccurrences', event.recurrence_occurrences)
        event.fee_amount = Decimal(data.get('fee_amount', event.fee_amount))
        event.fee_date = data.get('fee_date', event.fee_date)
        event.child_id = data.get('childId', event.child_id)
        event.trusted_person_id = data.get('trustedPersonId', event.trusted_person_id)

        event.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Event

@csrf_exempt
def submit_cancellation(request):
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        child_id = request.POST.get('child_id')
        date = request.POST.get('date')
        revoke = request.POST.get('revoke') == 'true'

        try:
            event = Event.objects.get(id=event_id, child=child_id)
            if event.event_cancelled_dates:
                event_cancelled_dates = event.event_cancelled_dates.split(',')
            else:
                event_cancelled_dates = []
            if revoke:
                if date in event_cancelled_dates:
                    event_cancelled_dates.remove(date)
                    event.event_cancelled_dates = ','.join(event_cancelled_dates)
                    event.save()
                    return JsonResponse({'status': 'success', 'message': 'Event cancellation revoked successfully'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Event not cancelled for this date'})
            else:
                if date not in event_cancelled_dates:
                    event_cancelled_dates.append(date)
                    event.event_cancelled_dates = ','.join(event_cancelled_dates)
                    event.save()
                    return JsonResponse({'status': 'success', 'message': 'Event cancelled successfully'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Event already cancelled for this date'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
