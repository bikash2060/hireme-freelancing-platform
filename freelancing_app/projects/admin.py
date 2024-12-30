# admin.py
from django.contrib import admin
from .models import SkillCategory, Skill, ProjectCategory

class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Fields to display in the admin list view
    search_fields = ('name',)      # Fields to search by

class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')  # Fields to display in the admin list view
    list_filter = ('category',)  # Filter by category
    search_fields = ('name',)    # Fields to search by

# Registering models with the custom admin class
admin.site.register(SkillCategory, SkillCategoryAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(ProjectCategory)
