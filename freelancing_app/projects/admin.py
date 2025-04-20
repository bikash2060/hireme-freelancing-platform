from django.contrib import admin
from .models import Skill, ProjectCategory, Project, ProjectAttachment

admin.site.register(Skill)
admin.site.register(ProjectCategory)
admin.site.register(Project)
admin.site.register(ProjectAttachment)