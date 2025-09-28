from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import StudyPlan, StudyDay

# Inline display for StudyDay under StudyPlan
class StudyDayInline(admin.TabularInline):
    model = StudyDay
    extra = 0  # Don't show extra empty forms
    readonly_fields = ('day_number', 'topic', 'is_completed')
    can_delete = True

# StudyPlan admin
@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ('subject', 'class_name', 'total_days', 'user', 'created_at')
    list_filter = ('subject', 'class_name', 'created_at')
    search_fields = ('subject', 'class_name', 'user__username')
    inlines = [StudyDayInline]

# Register StudyDay separately if you want
@admin.register(StudyDay)
class StudyDayAdmin(admin.ModelAdmin):
    list_display = ('plan', 'day_number', 'topic', 'is_completed')
    list_filter = ('plan', 'is_completed')
    search_fields = ('plan__subject', 'topic')
