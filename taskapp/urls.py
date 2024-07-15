# taskapp/urls.py

from django.urls import path

from . import views
from .forms import PasswordResetForm
from .views import home, signup, login_view, logout_view, add_child, header, calendar_view, save_event, \
    manage_children_view, add_trusted_person, view_events_by_child_and_date, submit_attendance, \
    profile, event_calendar, get_events, event_list, get_attendance_data, aboutus, fee_payment_view, user_events_view, \
    CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, \
    CustomPasswordResetCompleteView
from .views import EventListCreateView, EventRetrieveUpdateDestroyView
from django.contrib.auth import views as auth_views
from .views import ChildListCreateView, ChildRetrieveUpdateDestroyView, TrustedPersonListCreateView, TrustedPersonRetrieveUpdateDestroyView

urlpatterns = [
    path('', home, name='home'),
    path('header/', header, name='header'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('add_child/', add_child, name='add_child'),
    path('calendar/', calendar_view, name='calendar'),
    path('save_event/', save_event, name='save_event'),
    path('manage_children/', manage_children_view, name='manage_children'),
    path('add-trusted-person/', add_trusted_person, name='add_trusted_person'),

    path('api/events/', EventListCreateView.as_view(), name='event-list-create'),
    path('api/events/<int:pk>/', EventRetrieveUpdateDestroyView.as_view(), name='event-retrieve-update-destroy'),
    path('view_events_by_child_and_date/', view_events_by_child_and_date, name='view_events_by_child_and_date'),
    path('submit_attendance/', submit_attendance, name='submit_attendance'),
    # path('child_dashboard/', child_dashboard, name='child_dashboard'),
    path('profile/', profile, name='profile'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('get_events/', get_events, name='get_events'),
    path('eventcalendar/', views.event_calendar, name='event_calendar'),
    path('get_child_color/', views.get_child_color, name='get_child_color'),
    path('contact_view/',views.contact_view,name='contact_view'),
    path('success/', views.contact_success_view, name='contact_success'),








    # path('clas', views.classes_list, name='classes_list'),
    path('add/', views.add_class, name='add_class'),
    path('events/', event_list, name='event_list'),
    path('api/events/<int:event_id>/update/', views.update_event, name='update_event'),




    path('children/', ChildListCreateView.as_view(), name='child-list'),
    path('children/<int:pk>/', ChildRetrieveUpdateDestroyView.as_view(), name='child-detail'),
    path('trusted-people/', TrustedPersonListCreateView.as_view(), name='trustedperson-list'),
    path('trusted-people/<int:pk>/', TrustedPersonRetrieveUpdateDestroyView.as_view(), name='trustedperson-detail'),
    path('get_attendance_data/', get_attendance_data, name='get_attendance_data'),
    path('about_us/', aboutus, name='about_us'),
    path('events1/', user_events_view, name='user_events'),
    path('event/<int:event_id>/fee_payment/', fee_payment_view, name='fee_payment'),
    path('get_events_for_date/', views.get_events_for_date, name='get_events_for_date'),



    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('child/<int:child_id>/', views.child_activities_view, name='child_activities'),
    path('submit_cancellation/', views.submit_cancellation, name='submit_cancellation'),



]



