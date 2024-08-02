from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Basic fitness-related fields
    height = models.FloatField(null=True, blank=True, help_text="Height in centimeters")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kilograms")
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Fitness goals
    fitness_goal = models.CharField(max_length=100, blank=True, choices=[
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Endurance'),
        ('general_fitness', 'General Fitness'),
    ])
    
    # Activity level
    activity_level = models.CharField(max_length=50, blank=True, choices=[
        ('sedentary', 'Sedentary'),
        ('lightly_active', 'Lightly Active'),
        ('moderately_active', 'Moderately Active'),
        ('very_active', 'Very Active'),
        ('extra_active', 'Extra Active'),
    ])
    
    # Additional fields that might be useful
    preferred_workout_time = models.TimeField(null=True, blank=True)
    workout_reminder = models.BooleanField(default=False)
    
    # You can add more fields as needed

    def __str__(self):
        return self.username

    def get_bmi(self):
        if self.height and self.weight:
            return self.weight / ((self.height / 100) ** 2)
        return None

    # Add more methods as needed
