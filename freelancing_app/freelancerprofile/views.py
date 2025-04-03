from django.core.files.storage import FileSystemStorage
from accounts.mixins import CustomLoginRequiredMixin
from django.shortcuts import render, redirect
from accounts.models import City, Country
from django.http import JsonResponse
from django.contrib import messages
from projects.models import Skill
from django.conf import settings
from django.urls import reverse
from django.views import View
from datetime import datetime
from .models import *
from .utils import *

class GetCitiesByCountryView(View):
    def get(self, request, *args, **kwargs):
        country_id = request.GET.get('country_id')
        if not country_id:
            return JsonResponse({'cities': []})
        
        try:
            cities = City.objects.filter(country_id=country_id).order_by('name').values('id', 'name')
            return JsonResponse({'cities': list(cities)})
        except Exception as e:
            return JsonResponse({'cities': []})

class FreelancerBasicInfoView(CustomLoginRequiredMixin, View):
    profile_template = 'freelancerprofile/profile.html'
    home_url = 'home:home'

    def get(self, request):
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            freelancer_languages = FreelancerLanguage.objects.filter(freelancer=freelancer).select_related('language')
            experiences = WorkExperience.objects.filter(freelancer=freelancer).order_by('-start_date')
            return render(request, self.profile_template, {
                'freelancer': freelancer,
                'freelancer_languages': freelancer_languages,
                'experiences': experiences
            })
    
        except Exception as e:
            print('Exception:', e)
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
    personal_details_url = 'freelancer:edit-personal-info'
    
    def get(self, request):
        try:
            user = request.user
            user.profile_image = None
            user.save()
            messages.success(request, 'Your profile image has been deleted successfully!')
            return redirect(self.freelancer_profile_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.personal_details_url)

class EditFreelancerProfessionalInfoView(CustomLoginRequiredMixin, View):
    professional_info_template = 'freelancerprofile/editprofessionalinfo.html'
    professional_info_url = 'freelancer:edit-professional-info'
    freelancer_profile_url = 'freelancer:profile'

    def get(self, request):
        try:
            user = request.user
            freelancer = Freelancer.objects.get(user=user)
            all_skills = Skill.objects.all().order_by('name')
            selected_skills = freelancer.skills.values_list('id', flat=True)
            all_languages = Language.objects.all()
            
            language_proficiencies = {}
            for freelancer_language in FreelancerLanguage.objects.filter(freelancer=freelancer):
                language_proficiencies[freelancer_language.language.code] = freelancer_language.proficiency
            
            all_countries = Country.objects.all().order_by('name')
            current_country = user.country
            current_city = user.city

            return render(request, self.professional_info_template, {
                'freelancer': freelancer,
                'skills': all_skills,
                'skills_select': selected_skills,
                'all_languages': all_languages,
                'language_proficiencies': language_proficiencies,
                'countries': all_countries,
                'current_country': current_country.id if current_country else None,
                'current_city': current_city.id if current_city else None,
            })
            
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
    
    def post(self, request):
        try: 
            user = request.user
            freelancer = Freelancer.objects.get(user=request.user)
            all_skills = Skill.objects.all().order_by('name')
            all_languages = Language.objects.all()
            
            city_id = request.POST.get('city')
            country_id = request.POST.get('country')
            hourly_rate = request.POST.get('hourly_rate')
            selected_skills = request.POST.getlist('skills')
            selected_skills = [int(skill_id) for skill_id in selected_skills]

            language_proficiencies = {}
            for language in all_languages:
                proficiency_value = request.POST.get(f"{language.code}_proficiency")
                if proficiency_value:
                    language_proficiencies[language.code] = int(proficiency_value)
                    
            all_countries = Country.objects.all().order_by('name')
            current_country = Country.objects.filter(id=country_id).first() if country_id else None
            
            context = {
                'freelancer': freelancer,
                'skills': all_skills,
                'skills_select': selected_skills,
                'all_languages': all_languages,
                'language_proficiencies': language_proficiencies,
                'countries': all_countries,
                'current_country': current_country.id if current_country else None,
                'current_city': city_id,
                'submitted_data': {
                    'hourly_rate': hourly_rate,
                    'city_id': city_id,
                    'country_id': country_id,
                }
            }
            
            valid, error_message = validate_professional_info(city_id, country_id, hourly_rate, selected_skills, language_proficiencies)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.professional_info_template, context)

            if current_country:
                user.country = current_country
            if city_id:
                try:
                    city = City.objects.get(id=city_id)
                    user.city = city
                except City.DoesNotExist:
                    messages.error(request, 'Selected city is not valid')
                    return render(request, self.professional_info_template, context)
                
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
            return redirect(self.professional_info_url)
        
class AddFreelancerExperienceView(CustomLoginRequiredMixin, View):
    new_experience_template = 'freelancerprofile/addexperience.html'
    new_experience_url = 'freelancer:add-experience'
    freelancer_profile_url = 'freelancer:profile'
    
    def get(self, request):
        try:
            all_skills = Skill.objects.all().order_by('name')
            all_countries = Country.objects.all().order_by('name')
            return render(request, self.new_experience_template, {
                'skills': all_skills,
                'countries': all_countries,
            })
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
    
    def post(self, request):
        try:
            user = request.user
            freelancer = Freelancer.objects.get(user=user) 
            
            company_name = request.POST.get('company_name')
            job_title = request.POST.get('job_title')
            employment_type = request.POST.get('employment_type')
            start_date = request.POST.get('start_date')
            currently_working = request.POST.get('currently_working') == 'on'  
            end_date = request.POST.get('end_date') if not currently_working else None
            country_id = request.POST.get('country')
            city_id = request.POST.get('city')
            job_description = request.POST.get('job_description')
            selected_skill_ids = request.POST.getlist('skills')
            selected_skill_ids = [int(skill_id) for skill_id in selected_skill_ids]
            
            all_skills = Skill.objects.all().order_by('name')
            all_countries = Country.objects.all().order_by('name')
            current_country = Country.objects.filter(id=country_id).first() if country_id else None
            
            form_data={
                'company_name': company_name,
                'job_title': job_title,
                'employment_type': employment_type,
                'start_date': start_date,
                'currently_working': currently_working,
                'end_date': end_date,
                'countries': all_countries,
                'current_country': current_country.id if current_country else None,
                'current_city': city_id,
                'skills': all_skills,
                'skills_select': selected_skill_ids,
            }
            
            valid, error_message = validate_employment_data(company_name, job_title, employment_type, start_date,
                currently_working, end_date, country_id, city_id, selected_skill_ids
            )
            if not valid:
                messages.error(request, error_message)
                return render(request, self.new_experience_template, form_data)
            
            country = Country.objects.get(id=country_id)
            city = City.objects.get(id=city_id) if city_id else None
                
            start_date_parsed = datetime.strptime(start_date, '%Y-%m').date()
            end_date_parsed = datetime.strptime(end_date, '%Y-%m').date() if end_date else None
            
            experience = WorkExperience(
                freelancer=freelancer,
                company_name=company_name,
                job_title=job_title,
                employment_type=employment_type,
                start_date=start_date_parsed,
                end_date=end_date_parsed,
                currently_working=currently_working,
                country=country,
                city=city,
                description=job_description,
            )
            experience.save()
            
            experience.skills.set(selected_skill_ids)
            
            messages.success(request, 'Your work experience has been successfully added!')
            return redirect(self.freelancer_profile_url)
            
        except Exception:
            messages.error(request, 'Something went wrong while saving your experience.')
            return redirect(self.new_experience_url)
        
class EditFreelancerExperienceView(CustomLoginRequiredMixin, View):
    edit_experience_template = 'freelancerprofile/editexperience.html'
    edit_experience_url = 'freelancer:edit-experience'
    freelancer_profile_url = 'freelancer:profile'
    
    def get(self, request, experience_id):
        try:
            user = request.user
            freelancer = Freelancer.objects.get(user=user) 
            experience = WorkExperience.objects.get(id=experience_id, freelancer__user=request.user)
            all_skills = Skill.objects.all().order_by('name')
            all_countries = Country.objects.all().order_by('name')
            selected_skill_ids = list(experience.skills.values_list('id', flat=True))
            
            form_data = {
                'freelancer': freelancer,
                'experience': experience,
                'countries': all_countries,
                'skills': all_skills,
                'skills_select': selected_skill_ids,
            }
            
            return render(request, self.edit_experience_template, form_data)
            
        except WorkExperience.DoesNotExist:
            messages.error(request, 'Experience not found or you don\'t have permission to edit it.')
            return redirect(self.freelancer_profile_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
    
    def post(self, request, experience_id):
        try:
            experience = WorkExperience.objects.get(id=experience_id, freelancer__user=request.user)
            
            company_name = request.POST.get('company_name')
            job_title = request.POST.get('job_title')
            employment_type = request.POST.get('employment_type')
            start_date = request.POST.get('start_date')
            currently_working = request.POST.get('currently_working') == 'on'
            end_date = request.POST.get('end_date') if not currently_working else None
            country_id = request.POST.get('country')
            city_id = request.POST.get('city')
            job_description = request.POST.get('job_description')
            selected_skill_ids = request.POST.getlist('skills')
            selected_skill_ids = [int(skill_id) for skill_id in selected_skill_ids]
            
            all_skills = Skill.objects.all().order_by('name')
            all_countries = Country.objects.all().order_by('name')
            current_country = Country.objects.filter(id=country_id).first() if country_id else None
            
            form_data = {
                'experience_id': experience.id,
                'company_name': company_name,
                'job_title': job_title,
                'employment_type': employment_type,
                'start_date': start_date,
                'currently_working': currently_working,
                'end_date': end_date,
                'countries': all_countries,
                'current_country': current_country.id if current_country else None,
                'current_city': city_id,
                'job_description': job_description,
                'skills': all_skills,
                'skills_select': selected_skill_ids,
            }
            
            valid, error_message = validate_employment_data(
                company_name, job_title, employment_type, start_date,
                currently_working, end_date, country_id, city_id, selected_skill_ids
            )
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.edit_experience_template, form_data)
            
            country = Country.objects.get(id=country_id)
            city = City.objects.get(id=city_id) if city_id else None
            
            start_date_parsed = datetime.strptime(start_date, '%Y-%m').date()
            end_date_parsed = datetime.strptime(end_date, '%Y-%m').date() if end_date else None
            
            experience.company_name = company_name
            experience.job_title = job_title
            experience.employment_type = employment_type
            experience.start_date = start_date_parsed
            experience.end_date = end_date_parsed
            experience.currently_working = currently_working
            experience.country = country
            experience.city = city
            experience.description = job_description
            experience.save()
            
            experience.skills.set(selected_skill_ids)
            
            messages.success(request, 'Your work experience has been successfully updated!')
            return redirect(self.freelancer_profile_url)
            
        except WorkExperience.DoesNotExist:
            messages.error(request, 'Experience not found or you don\'t have permission to edit it.')
            return redirect(self.freelancer_profile_url)
        except Exception:
            messages.error(request, 'Something went wrong while updating your experience.')
            return redirect(reverse(self.edit_experience_url, kwargs={'experience_id': experience_id}))