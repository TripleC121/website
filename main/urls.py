from django.contrib.auth.views import LogoutView
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("learning/", views.learning, name="learning"),
    path("learning/full_stack/", views.full_stack, name="full_stack"),
    path("learning/full_stack/cloud_tech", views.cloud_tech, name="cloud_tech"),
    path(
        "learning/full_stack/devops_overview",
        views.devops_overview,
        name="devops_overview",
    ),
    path(
        "learning/full_stack/frontend_overview",
        views.frontend_overview,
        name="frontend_overview",
    ),
    path(
        "learning/full_stack/django_details",
        views.django_details,
        name="django_details",
    ),
    path("learning/pgp_aiml/", views.pgp_aiml, name="pgp_aiml"),
    path(
        "learning/pgp_aiml/ai_foundations", views.ai_foundations, name="ai_foundations"
    ),
    path(
        "learning/pgp_aiml/machine_learning",
        views.machine_learning,
        name="machine_learning",
    ),
    path("learning/pgp_aiml/deep_learning", views.deep_learning, name="deep_learning"),
    path(
        "learning/pgp_aiml/course_projects/",
        views.course_projects,
        name="course_projects",
    ),
    path("learning/pgp_aiml/project1", views.project1, name="project1"),
    path("learning/pgp_aiml/project2", views.project2, name="project2"),
    path("learning/pgp_aiml/project3", views.project3, name="project3"),
    path("learning/pgp_aiml/project4", views.project4, name="project4"),
    path("learning/pgp_aiml/project5", views.project5, name="project5"),
    path("learning/pgp_aiml/project6", views.project6, name="project6"),
    path("technology/", views.technology_view, name="technology"),
    path("technology/cloud/", views.cloud_technologies_view, name="cloud_technologies"),
    path("technology/devops-cicd/", views.devops_cicd_view, name="devops_cicd"),
    path(
        "technology/backend/",
        views.backend_technologies_view,
        name="backend_technologies",
    ),
    path(
        "technology/frontend/",
        views.frontend_technologies_view,
        name="frontend_technologies",
    ),
    path("technology/", views.technology_view, name="technology"),
    path("technology/cloud/", views.cloud_technologies_view, name="cloud_technologies"),
    path("technology/devops-cicd/", views.devops_cicd_view, name="devops_deployment"),
    path("growing/", views.growing, name="growing"),
    path("growing/succulents/", views.succulents, name="succulents"),
    path("growing/trees/", views.trees_index, name="growing_trees_index"),
    path(
        "growing/trees/meyer-lemon/",
        views.meyer_lemon_tree,
        name="growing_trees_meyer_lemon",
    ),
    path("growing/trees/avocado/", views.avocado_tree, name="growing_trees_avocado"),
    path("growing/trees/fig/", views.fig_tree, name="growing_trees_fig"),
    path(
        "growing/trees/pomegranate/",
        views.pomegranate_tree,
        name="growing_trees_pomegranate",
    ),
    path("about/", views.about, name="about"),
    path("about/why/", views.about_why, name="about_why"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("signup/", views.signup, name="signup"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password_reset/",
        views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        views.CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
