#taskapp/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django_countries import countries
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from taskapp.models import Child, TrustedPerson
from .models import CustomUser


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    phone_number = forms.CharField(max_length=15, help_text='Required. Enter your phone number.',label='Phone Number')

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']



class LoginForm(AuthenticationForm):
    class Meta:
        model = User

# taskapp/forms.py

from django import forms
from .models import Child

class AttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    child = forms.ModelChoiceField(queryset=Child.objects.all())
    attended = forms.BooleanField(required=False)
    def __init__(self, user, *args, **kwargs):
        user = kwargs.pop('user', None)
        user_children = kwargs.pop('user_children', None)
        super(AttendanceForm, self).__init__(*args, **kwargs)

        if user_children:
            self.fields['child'].queryset = user_children
        self.user = user


# class ChildForm(forms.ModelForm):
#     GENDER_CHOICES = (
#         ('M', 'Male'),
#         ('F', 'Female'),
#         ('O', 'Prefer Not to disclose'),
#     )
#
#     gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select())
#     age=forms.CheckboxInput()
#     class Meta:
#         model = Child
#         fields = ['name', 'gender', 'dob','interests']
class TrustedPersonForm(forms.ModelForm):
    phone_country_code = forms.ChoiceField(choices=[('+' + code, f"{name} (+{code})") for code, name in countries],
                                           initial='+91',
    widget=forms.Select(attrs={'class': 'custom-select'}))

    class Meta:
        model = TrustedPerson
        fields = ['name', 'relation', 'phone_country_code', 'phone_number']

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class ProfileForm(UserChangeForm):
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput,
        required=False,
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput,
        required=False,
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': ' mt-2 bg-white w-full border-2 border-[#f1f5f9] text-[#e2e8f0] rounded-lg h-[50px] text-lg   lg:text-sm','style':'color: #6b7280'}),
            'email': forms.EmailInput(attrs={'class': ' mt-2 bg-white w-full border-2 border-[#f1f5f9] text-[#e2e8f0] rounded-lg h-[50px] text-lg   lg:text-sm','style':'color: #6b7280'}),
            'phone_number': forms.TextInput(attrs={'class': ' mt-2 bg-white w-full border-2 border-[#f1f5f9] text-[#e2e8f0] rounded-lg h-[50px] text-lg   lg:text-sm','style':'color: #6b7280'}),
        }

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if current_password and not self.user.check_password(current_password):
            raise ValidationError('Incorrect current password')
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError('New passwords do not match')

# forms.py
from django import forms
from .models import Class

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['title', 'description', 'image']
# forms.py
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


from django import forms
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives

class PasswordResetForm(DjangoPasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name:
            html_email = render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name='registration/password_reset_email.html',
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the user.
        """
        email = self.cleaned_data["email"]
        UserModel = get_user_model()
        active_users = UserModel._default_manager.filter(
            email__iexact=email, is_active=True)

        for user in active_users:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                email, html_email_template_name=html_email_template_name,
            )
