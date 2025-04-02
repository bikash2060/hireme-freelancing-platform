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
            educations = list(Education.objects.filter(freelancer_id=freelancer))
            certificates = list(Certificate.objects.filter(freelancer_id=freelancer)) 

            experience_years = freelancer.experience_years
            if experience_years is not None:
                if experience_years == 0:
                    experience_display = "Less than a year"
                elif experience_years == 1:
                    experience_display = "1+ year"
                else:
                    experience_display = f"{experience_years}+ years"
            else:
                experience_display = "Not Provided"

            current_date = datetime.now()

            educations_with_duration = []
            if educations:
                for edu in educations:
                    educations_with_duration.append({
                        'education': edu,
                        'is_current': edu.end_date is None,
                        'start_date': edu.start_date,
                        'end_date': edu.end_date or current_date,
                    })
                educations_with_duration.sort(key=lambda x: (
                    not x['is_current'],  
                    -datetime.combine(x['start_date'], datetime.min.time()).timestamp() if x['is_current'] else -datetime.combine(x['end_date'], datetime.min.time()).timestamp()
                ))

            certificates_sorted = []
            if certificates:
                certificates_sorted = sorted(certificates, key=lambda x: x.issued_date, reverse=True)

            return render(request, self.profile_template, {
                'freelancer': freelancer,
                'experience_display': experience_display,
                'educations_with_duration': educations_with_duration,
                'certificates': certificates_sorted,  
                'current_year': current_date.year
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
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            sorted_cities = sorted(settings.NEPALI_CITIES) 
            all_skills = Skill.objects.all().order_by('name')
            return render(request, self.professional_info_template, {
                'freelancer': freelancer,
                'cities': sorted_cities,
                'all_skills': all_skills
            })
        except Exception as e:
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.freelancer_profile_url)
        
    