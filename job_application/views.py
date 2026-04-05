from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .forms import JobApplicationForm, RegisterForm
from .models import JobApplication


# ✅ HOME VIEW (Apply Job + Email + Popup)
def home(request):
    form = JobApplicationForm()

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            app = form.save()

            # 📧 Send Email Safely
            try:

                from django.core.mail import EmailMultiAlternatives
                from django.template.loader import render_to_string
                from django.utils.html import strip_tags

                # inside your home view
                if form.is_valid():
                    app = form.save()

                # 🎨 Render HTML email
                html_content = render_to_string('job_application/email_template.html', {
                    'name': app.first_name,
                    'job': app.job_title,
                })

                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject='Application Received - Myjob Enterprise',
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[app.email],
                )

                email.attach_alternative(html_content, "text/html")
                email.send()
            except Exception as e:
                messages.warning(request, "Application saved, but email failed to send.")

            # ✅ Success Message
            messages.success(request, f"Thank you {app.first_name}! Your application has been submitted.")

            return redirect('home')

        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'job_application/index.html', {'form': form})


# ✅ SUCCESS PAGE (optional)
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


# ✅ DASHBOARD (Protected)
@login_required
def dashboard(request):
    applications = JobApplication.objects.all()
    return render(request, 'job_application/dashboard.html', {'apps': applications})

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')

    return render(request, 'job_application/login.html', {'form': form})

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')

    return render(request, 'job_application/login.html', {'form': form})