from django.urls import path
from . import views

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
   # path('reading/', views.reading, name='reading'),
   # path('cooking/', views.cooking, name='cooking'),
   # path('exercise/', views.exercise, name='exercise'),
]