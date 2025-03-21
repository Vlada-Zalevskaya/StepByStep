from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Frequency, Habit, Category, HabitCategory, Completion

admin.site.register(User)
admin.site.register(Frequency)
admin.site.register(Habit)
admin.site.register(Category)
admin.site.register(HabitCategory)
admin.site.register(Completion)