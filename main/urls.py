from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views
from .views import TechnologyView, CICDDetailsView

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('learning/', views.learning, name='learning'),
    path('learning/full_stack/', views.full_stack, name='full_stack'),
    path('learning/pgp_aiml/', views.pgp_aiml, name='pgp_aiml'),
    path('learning/pgp_aiml/project1', views.project1, name='project1'),
    path('learning/pgp_aiml/project2', views.project2, name='project2'),
    path('learning/pgp_aiml/project3', views.project3, name='project3'),
    path('learning/pgp_aiml/project4', views.project4, name='project4'),
    path('learning/pgp_aiml/project5', views.project5, name='project5'),
    path('growing/', views.growing, name='growing'),
    path('growing/succulents/', views.succulents, name='succulents'),
    path('growing/trees/', views.trees, name='trees'),
    path('about/', views.about, name='about'),
    path('user_test/', views.user_test, name='user_test'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('technology/', TechnologyView.as_view(), name='technology'),
    path('technology/cicd/', CICDDetailsView.as_view(), name='cicd_details'),
]
