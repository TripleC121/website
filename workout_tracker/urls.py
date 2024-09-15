from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExerciseViewSet, WorkoutViewSet, WorkoutExerciseViewSet

router = DefaultRouter()
router.register(r'exercises', ExerciseViewSet)
router.register(r'workouts', WorkoutViewSet)
router.register(r'workout-exercises', WorkoutExerciseViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
