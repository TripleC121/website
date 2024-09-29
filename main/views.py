import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from .forms import CustomUserCreationForm

logger = logging.getLogger(__name__)


def homepage(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about/index.html")


def about_why(request):
    return render(request, "about/why.html")


def learning(request):
    return render(request, "learning/index.html")


def full_stack(request):
    return render(request, "learning/full_stack/index.html")


def cloud_tech(request):
    return render(request, "learning/full_stack/cloud_tech.html")


def devops_overview(request):
    return render(request, "learning/full_stack/devops_overview.html")


def django_details(request):
    return render(request, "learning/full_stack/django_details.html")


def frontend_overview(request):
    return render(request, "learning/full_stack/frontend_overview.html")


def pgp_aiml(request):
    return render(request, "learning/pgp_aiml/index.html")


def ai_foundations(request):
    return render(request, "learning/pgp_aiml/ai_foundations.html")


def machine_learning(request):
    return render(request, "learning/pgp_aiml/machine_learning.html")


def deep_learning(request):
    return render(request, "learning/pgp_aiml/deep_learning.html")


def course_projects(request):
    return render(request, "learning/pgp_aiml/course_projects.html")


def project1(request):
    return render(request, "learning/pgp_aiml/project1.html")


def project2(request):
    return render(request, "learning/pgp_aiml/project2.html")


def project3(request):
    return render(request, "learning/pgp_aiml/project3.html")


def project4(request):
    return render(request, "learning/pgp_aiml/project4.html")


def project5(request):
    return render(request, "learning/pgp_aiml/project5.html")


def technology_view(request):
    return render(request, "technology/index.html")


def cloud_technologies_view(request):
    return render(request, "technology/cloud_technologies.html")


def devops_cicd_view(request):
    return render(request, "technology/devops_cicd.html")


def backend_technologies_view(request):
    return render(request, "technology/backend_technologies.html")


def frontend_technologies_view(request):
    return render(request, "technology/frontend_technologies.html")


def growing(request):
    return render(request, "growing/index.html")


def succulents(request):
    return render(request, "growing/succulents/index.html")


def trees(request):
    return render(request, "growing/trees/index.html")


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("homepage")
    else:
        form = CustomUserCreationForm()
    return render(request, "signup.html", {"form": form})


# Password reset views
class CustomPasswordResetView(PasswordResetView):
    template_name = "password_reset/password_reset_form.html"
    email_template_name = "password_reset/password_reset_email.html"
    subject_template_name = "password_reset/password_reset_subject.txt"
    success_url = "/password_reset/done/"


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "password_reset/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "password_reset/password_reset_confirm.html"
    success_url = "/password_reset/complete/"


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "password_reset/password_reset_complete.html"
