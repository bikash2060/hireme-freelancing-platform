from django.shortcuts import render, redirect
from django.views import View
from projects.models import Skill

# Testing In-Progress
class FreelancerListView(View):
    
    rendered_template = 'freelancers/freelancerslist.html'
    
    def get(self, request):
        skills = Skill.objects.all().order_by('name')
        
        context = {
            'skills': skills
        }
        return render(request, self.rendered_template, context)