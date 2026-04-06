from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import threading

from .forms import JobApplicationForm, RegisterForm
from .models import JobApplication


# 🔥 SEND EMAIL IN BACKGROUND (NO TIMEOUT)
def send_email_async(email):
    email.send(fail_silently=True)


# ✅ HOME VIEW
def home(request):
    form = JobApplicationForm()

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            app = form.save()

            try:
                # 🎨 HTML email
                html_content = render_to_string(
                    'job_application/email_template.html',
                    {
                        'name': app.first_name,
                        'job': app.job_title,
                    }
                )

                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject='Application Received - MY_JOBS',
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[app.email],
                    reply_to=[settings.DEFAULT_FROM_EMAIL],
                )

                email.attach_alternative(html_content, "text/html")

                # 🚀 NON-BLOCKING EMAIL
                threading.Thread(target=send_email_async, args=(email,)).start()

            except Exception:
                messages.warning(request, "Application saved, but email failed.")

            messages.success(
                request,
                f"Thank you {app.first_name}! Your application has been submitted."
            )

            return redirect('home')

        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'job_application/index.html', {'form': form})


# ✅ SUCCESS PAGE
def success(request):
    return render(request, 'job_application/success.html')


# ✅ ABOUT PAGE
def about(request):
    return render(request, 'job_application/about.html')


# ✅ REGISTER USER
def register_view(request):
    form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, 'job_application/register.html', {'form': form})


# ✅ LOGIN VIEW
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')

    return render(request, 'job_application/login.html', {'form': form})


# ✅ DASHBOARD (Protected)
@login_required
def dashboard(request):
    applications = JobApplication.objects.all()
    return render(request, 'job_application/dashboard.html', {'apps': applications})