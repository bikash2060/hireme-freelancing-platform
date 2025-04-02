from django.core.files.storage import FileSystemStorage
from accounts.mixins import CustomLoginRequiredMixin
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from projects.models import Skill
from datetime import datetime
from django.views import View
from django.conf import settings
from .utils import *

class FreelancerBasicInfoView(CustomLoginRequiredMixin, View):
    profile_template = 'freelancerprofile/profile.html'
    home_url = 'home:home'

    def get(self, request):
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            freelancer_languages = FreelancerLanguage.objects.filter(freelancer=freelancer).select_related('language')
            return render(request, self.profile_template, {
                'freelancer': freelancer,
                'freelancer_languages': freelancer_languages
            })
    
        except Exception:
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.home_url)

class EditFreelancerPersonalInfoView(CustomLoginRequiredMixin, View):
    personal_details_template = 'freelancerprofile/editpersonalinfo.html'
    personal_details_url = 'freelancer:edit-personal-info'
    freelancer_profile_url = 'freelancer:profile'

    def get(self, request):
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            return render(request, self.personal_details_template, {'freelancer': freelancer})
        except Exception:
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.freelancer_profile_url)

    def post(self, request):
        try:
            user = request.user
            
            profile_image = request.FILES.get('profile_image')
            full_name = request.POST.get('full_name').strip()
            username = request.POST.get('username').strip().lower()
            phone_number = request.POST.get('phone_number').strip()
            bio = request.POST.get('bio').strip()
            
            form_data = {
                'full_name': full_name,
                'username': username,
                'phone_number': phone_number,
                'bio': bio
            }
            
            valid, error_message = validate_user_data(profile_image, full_name, username, phone_number, bio, request)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.personal_details_template, {
                    'form_data': form_data
                })

            if profile_image:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'profile_images'))
                filename = fs.save(profile_image.name, profile_image)
                user.profile_image = filename.split('/')[-1]
                
            user.full_name = full_name
            user.username = username
            user.phone_number = phone_number
            user.bio = bio

            user.save()    
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect(self.freelancer_profile_url)
            
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.personal_details_url)

class DeleteProfileImageView(CustomLoginRequiredMixin, View):
    freelancer_profile_url = 'freelancer:profile'

    def get(self, request):
        try:
            user = request.user
            user.profile_image = None
            user.save()
            messages.success(request, 'Your profile image has been deleted successfully!')
            return redirect(self.freelancer_profile_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
        
class EditFreelancerProfessionalInfoView(CustomLoginRequiredMixin, View):
    professional_info_template = 'freelancerprofile/editprofessionalinfo.html'
    freelancer_profile_url = 'freelancer:profile'

    def get(self, request):
            freelancer = Freelancer.objects.get(user=request.user)
            sorted_cities = sorted(settings.NEPALI_CITIES)
            all_skills = Skill.objects.all().order_by('name')
            selected_skills = freelancer.skills.values_list('id', flat=True)
            all_languages = Language.objects.all()
            
            language_proficiencies = {}
            for freelancer_language in FreelancerLanguage.objects.filter(freelancer=freelancer):
                language_proficiencies[freelancer_language.language.code] = freelancer_language.proficiency
            
            return render(request, self.professional_info_template, {
                'freelancer': freelancer,
                'cities': sorted_cities,
                'skills': all_skills,
                'skills_select': selected_skills,
                'all_languages': all_languages,
                'language_proficiencies': language_proficiencies,
            })
    
    def post(self, request):
        try: 
            user = request.user
            freelancer = Freelancer.objects.get(user=request.user)
            all_skills = Skill.objects.all().order_by('name')
            all_languages = Language.objects.all()
            
            city = request.POST.get('city')
            hourly_rate = request.POST.get('hourly_rate')
            selected_skills = request.POST.getlist('skills')
            selected_skills = [int(skill_id) for skill_id in selected_skills]

            language_proficiencies = {}
            for language in all_languages:
                proficiency_value = request.POST.get(f"{language.code}_proficiency")
                if proficiency_value:
                    language_proficiencies[language.code] = int(proficiency_value)
            
            context = {
                'freelancer': freelancer,
                'cities': sorted(settings.NEPALI_CITIES),
                'skills': all_skills,
                'skills_select': selected_skills,
                'all_languages': all_languages,
                'language_proficiencies': language_proficiencies,
            }
            
            if not city or city not in settings.NEPALI_CITIES:
                messages.error(request, "Please select a valid city from the list")
                return render(request, self.professional_info_template, context)
            
            if not hourly_rate:
                messages.error(request, "Hourly rate is required")
                return render(request, self.professional_info_template, context)
                
            if not selected_skills or len(selected_skills) < 1:
                messages.error(request, "Please select at least one skill")
                return render(request, self.professional_info_template, context)
            
            user.city = city
            user.country = 'Nepal'
            freelancer.hourly_rate = hourly_rate
            
            freelancer.skills.clear()
            skills = Skill.objects.filter(id__in=selected_skills)
            freelancer.skills.add(*skills)
            
            FreelancerLanguage.objects.filter(freelancer=freelancer).delete()
            for language_code, proficiency_level in language_proficiencies.items():
                try:
                    language = Language.objects.get(code=language_code)
                    print('Language:', language)
                    FreelancerLanguage.objects.create(
                        freelancer=freelancer,
                        language=language,
                        proficiency=proficiency_level
                    )
                except Language.DoesNotExist:
                    continue
            
            user.save()
            freelancer.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect(self.freelancer_profile_url)
            
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)