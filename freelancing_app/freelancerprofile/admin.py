from django.contrib import admin
from .models import Language, FreelanceServiceCategory, Freelancer, FreelancerLanguage, WorkExperience, Education

admin.site.register(Language)
admin.site.register(FreelanceServiceCategory)
admin.site.register(Freelancer)
admin.site.register(FreelancerLanguage)
admin.site.register(WorkExperience)
admin.site.register(Education)