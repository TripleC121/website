from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ExerciseViewSet, WorkoutExerciseViewSet, WorkoutViewSet

router = DefaultRouter()
router.register(r"exercises", ExerciseViewSet)
router.register(r"workouts", WorkoutViewSet)
router.register(r"workout-exercises", WorkoutExerciseViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
