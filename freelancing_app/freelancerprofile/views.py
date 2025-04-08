from django.contrib.auth import update_session_auth_hash
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
from itertools import chain
from .models import *
from .utils import *

class GetCitiesByCountryView(CustomLoginRequiredMixin, View):
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
            
            experiences = WorkExperience.objects.filter(freelancer=freelancer)
            ongoing_experiences = experiences.filter(currently_working=True).order_by('-start_date')
            past_experiences = experiences.filter(currently_working=False).order_by(
                '-end_date' if WorkExperience._meta.get_field('end_date').null else 'end_date'
            )
            ordered_experiences = list(chain(ongoing_experiences, past_experiences))
            
            educations = Education.objects.filter(freelancer=freelancer)
            ongoing_educations = educations.filter(currently_studying=True).order_by('-start_date')
            past_educations = educations.filter(currently_studying=False).order_by(
                '-end_date' if Education._meta.get_field('end_date').null else 'end_date'
            )
            ordered_educations = list(chain(ongoing_educations, past_educations))
            
            return render(request, self.profile_template, {
                'freelancer': freelancer,
                'freelancer_languages': freelancer_languages,
                'experiences': ordered_experiences,
                'educations': ordered_educations,  
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
            user = request.user
            freelancer = Freelancer.objects.get(user=request.user)
            all_countries = Country.objects.all().order_by('name')
            current_country = user.country.id if user.country else None
            current_city = user.city.id if user.city else None
            
            return render(request, self.personal_details_template, {
                'freelancer': freelancer,
                'countries': all_countries,
                'current_country': current_country,
                'current_city': current_city,
            })
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)

    def post(self, request):
        try:
            user = request.user
            freelancer = Freelancer.objects.get(user=request.user)
            all_countries = Country.objects.all().order_by('name')
            
            profile_image = request.FILES.get('profile_image')
            full_name = request.POST.get('full_name').strip()
            username = request.POST.get('username').strip().lower()
            phone_number = request.POST.get('phone_number').strip()
            city_id = request.POST.get('city')
            country_id = request.POST.get('country')
            bio = request.POST.get('bio').strip()
            
            context = {
                'freelancer': freelancer,
                'full_name': full_name if full_name else None,
                'username': username if username else None, 
                'phone_number': phone_number if phone_number else None,
                'bio': bio if bio else None,
                'countries': all_countries,
                'current_country': int(country_id) if country_id else None,
                'current_city': int(city_id) if city_id else None,
            }
            
            valid, error_message = validate_user_data(profile_image, full_name, username, phone_number, bio, city_id, country_id, request)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.personal_details_template, context)
            
            if country_id:
                try:
                    country = Country.objects.get(id=country_id)
                    user.country = country
                except Country.DoesNotExist:
                    messages.error(request, 'Selected country is not valid')
                    return render(request, self.professional_info_template, context)
            
            if city_id:
                try:
                    city = City.objects.get(id=city_id)
                    user.city = city
                except City.DoesNotExist:
                    messages.error(request, 'Selected city is not valid')
                    return render(request, self.professional_info_template, context)

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
            
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.personal_details_url)

class DeleteProfileImageView(CustomLoginRequiredMixin, View):
    freelancer_profile_url = 'freelancer:profile'
    personal_details_url = 'freelancer:edit-personal-info'
    
    def get(self, request):
        try:
            user = request.user
            
            if user.profile_image:
                file_path = os.path.join(settings.MEDIA_ROOT, 'profile_images', str(user.profile_image.name))
                
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
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
            language_proficiencies_list = []
            for language in all_languages:
                proficiency = FreelancerLanguage.objects.filter(
                    freelancer=freelancer, 
                    language=language
                ).values_list('proficiency', flat=True).first()
                language_proficiencies_list.append({
                    'code': language.code,
                    'name': language.name,
                    'proficiency': proficiency if proficiency else None
                })

            return render(request, self.professional_info_template, {
                'freelancer': freelancer,
                'skills': all_skills,
                'skills_select': selected_skills,
                'all_languages': all_languages,
                'language_proficiencies_list': language_proficiencies_list
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

            hourly_rate = request.POST.get('hourly_rate')
            years_of_experience = request.POST.get('years_of_experience')
            expertise_level = request.POST.get('expertise_level')
            availability = request.POST.get('availability')
            preferred_project_duration = request.POST.get('preferred_project_duration')
            communication_preference = request.POST.get('communication_preference')
            
            selected_skills = request.POST.getlist('skills')
            selected_skills = [int(skill_id) for skill_id in selected_skills]

            language_proficiencies = {}
            language_proficiencies_list = []
            for language in all_languages:
                proficiency_value = request.POST.get(f"{language.code}_proficiency")
                if proficiency_value:
                    language_proficiencies[language.code] = int(proficiency_value)
                    
                language_proficiencies_list.append({
                    'code': language.code,
                    'name': language.name,
                    'proficiency': int(proficiency_value) if proficiency_value else None
                })

            context = {
                'freelancer': freelancer,
                'skills': all_skills,
                'skills_select': selected_skills,
                'all_languages': all_languages,
                'language_proficiencies_list': language_proficiencies_list, 
                'hourly_rate': hourly_rate,
                'years_of_experience': years_of_experience,
                'expertise_level': expertise_level,
                'availability': availability,
                'preferred_project_duration': preferred_project_duration,
                'communication_preference': communication_preference,
            }
            
            valid, error_message = validate_professional_info(
                hourly_rate, 
                years_of_experience,
                expertise_level,
                availability,
                preferred_project_duration,
                communication_preference,
                selected_skills, 
                language_proficiencies
            )
            if not valid:
                messages.error(request, error_message)
                return render(request, self.professional_info_template, context)
                
            freelancer.hourly_rate = hourly_rate
            freelancer.years_of_experience = years_of_experience if years_of_experience else 0
            freelancer.expertise_level = expertise_level
            freelancer.availability = availability
            freelancer.preferred_project_duration = preferred_project_duration
            freelancer.communication_preference = communication_preference
            
            freelancer.skills.clear()
            skills = Skill.objects.filter(id__in=selected_skills)
            freelancer.skills.add(*skills)
            
            FreelancerLanguage.objects.filter(freelancer=freelancer).delete()
            for language_code, proficiency_level in language_proficiencies.items():
                try:
                    language = Language.objects.get(code=language_code)
                    FreelancerLanguage.objects.create(
                        freelancer=freelancer,
                        language=language,
                        proficiency=proficiency_level
                    )
                except Language.DoesNotExist:
                    continue
                
            user.save()
            freelancer.save()
            messages.success(request, "Your professional information has been updated successfully!")
            return redirect(self.freelancer_profile_url)
            
        except Exception:
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
            
            form_data={
                'company_name': company_name,
                'job_title': job_title,
                'employment_type': employment_type,
                'start_date': start_date,
                'currently_working': currently_working,
                'end_date': end_date,
                'job_description': job_description,
                'countries': all_countries,
                'current_country': int(country_id) if country_id else None,
                'current_city': int(city_id) if city_id else None,
                'skills': all_skills,
                'skills_select': selected_skill_ids,
            }
            
            valid, error_message = validate_employment_data(company_name, job_title, employment_type, start_date,
                currently_working, end_date, country_id, city_id, selected_skill_ids
            )
            if not valid:
                messages.error(request, error_message)
                return render(request, self.new_experience_template, form_data)
            
            country = Country.objects.get(id=country_id) if country_id else None
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
            
            current_country = experience.country.id if user.country else None
            current_city = experience.city.id if user.city else None
            
            form_data = {
                'freelancer': freelancer,
                'experience': experience,
                'countries': all_countries,
                'current_country': current_country,
                'current_city': current_city,
                'skills': all_skills,
                'skills_select': selected_skill_ids,
            }
            return render(request, self.edit_experience_template, form_data)

        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
    
    def post(self, request, experience_id):
        try:
            user = request.user
            freelancer = Freelancer.objects.get(user=request.user)
            experience = WorkExperience.objects.get(id=experience_id, freelancer__user=user)
            
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
            
            form_data = {
                'freelancer': freelancer,
                'experience': experience,
                'company_name': company_name,
                'job_title': job_title,
                'employment_type': employment_type,
                'start_date': start_date,
                'currently_working': currently_working,
                'end_date': end_date,
                'countries': all_countries,
                'current_country': int(country_id) if country_id else None,
                'current_city': int(city_id) if city_id else None,
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
            
            country = Country.objects.get(id=country_id) if country_id else None
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
            
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.edit_experience_url, experience_id=experience_id)
        
class DeleteFreelancerExperienceView(CustomLoginRequiredMixin, View):
    freelancer_profile_url = 'freelancer:profile'
    
    def get(self, request, experience_id):
        try:
            experience = WorkExperience.objects.get(
                id=experience_id, 
                freelancer__user=request.user
            )
            experience.delete()
            
            messages.success(request, 'Your work experience has been successfully deleted!')
            return redirect(self.freelancer_profile_url)
                    
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
       
class AddFreelancerEducationView(CustomLoginRequiredMixin, View):
    add_education_template = 'freelancerprofile/addeducation.html'
    add_education_url = 'freelancer:add-education'
    freelancer_profile_url = 'freelancer:profile'
    
    def get(self, request):
        try:
            return render(request, self.add_education_template)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
        
    def post(self, request):
        try:
            user = request.user
            freelancer = Freelancer.objects.get(user=user)
            
            institution = request.POST.get('institution')
            degree = request.POST.get('degree')
            gpa = request.POST.get('gpa')
            start_date = request.POST.get('start_date')
            currently_studying = request.POST.get('currently_studying') == 'on'  
            end_date = request.POST.get('end_date') if not currently_studying else None
            
            context = {
                'institution': institution,
                'degree': degree,
                'gpa': gpa,
                'start_date': start_date,
                'currently_studying': currently_studying,
                'end_date': end_date,
            }
            
            valid, error_message = validate_education_data(institution, degree, start_date, currently_studying, end_date, gpa)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.add_education_template, context)
            
            start_date_parsed = datetime.strptime(start_date, '%Y-%m').date()
            end_date_parsed = datetime.strptime(end_date, '%Y-%m').date() if end_date else None
            
            education = Education(
                freelancer=freelancer,
                institution=institution,
                degree=degree,
                gpa=float(gpa) if gpa else None,
                start_date=start_date_parsed,
                end_date=end_date_parsed,
                currently_studying=currently_studying,
            )
            education.save()
            
            messages.success(request, 'Your education has been successfully added!')
            return redirect(self.freelancer_profile_url)     
            
        except Exception:
            messages.error(request, 'Something went wrong while saving your experience.')
            return redirect(self.add_education_url)

class EditFreelancerEducationView(CustomLoginRequiredMixin, View):
    edit_education_template = 'freelancerprofile/editeducation.html'
    edit_education_url = 'freelancer:edit-education'
    freelancer_profile_url = 'freelancer:profile'
    
    def get(self, request, education_id):
        try:
            user = request.user
            freelancer = Freelancer.objects.get(user=user) 
            education = Education.objects.get(id=education_id, freelancer__user=user)
            
            return render(request, self.edit_education_template, {
                'freelancer': freelancer,
                'education': education
            })
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
       
    def post(self, request, education_id):
        try:
            user = request.user
            freelancer = Freelancer.objects.get(user=user) 
            education = Education.objects.get(id=education_id, freelancer__user=user)
            
            institution = request.POST.get('institution')
            degree = request.POST.get('degree')
            gpa = request.POST.get('gpa')
            start_date = request.POST.get('start_date')
            currently_studying = request.POST.get('currently_studying') == 'on'  
            end_date = request.POST.get('end_date') if not currently_studying else None
            
            context = {
                'freelancer': freelancer,
                'education': education,
                'institution': institution,
                'degree': degree,
                'gpa': gpa,
                'start_date': start_date,
                'currently_studying': currently_studying,
                'end_date': end_date,
            }
            
            valid, error_message = validate_education_data(institution, degree, start_date, currently_studying, end_date, gpa)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.edit_education_template, context)
            
            start_date_parsed = datetime.strptime(start_date, '%Y-%m').date()
            end_date_parsed = datetime.strptime(end_date, '%Y-%m').date() if end_date else None
            
            education.institution = institution
            education.degree = degree
            education.gpa = float(gpa) if gpa else None
            education.start_date = start_date_parsed
            education.end_date = end_date_parsed
            education.currently_studying = currently_studying
            education.save()
            
            messages.success(request, 'Your education has been successfully updated!')
            return redirect(self.freelancer_profile_url)
            
        except Exception as e:
                print('Exception:', e)
                messages.error(request, 'Something went wrong. Please try again later.')
                return redirect(self.edit_education_url, education_id=education_id)

class DeleteFreelancerEducationView(CustomLoginRequiredMixin, View):
    freelancer_profile_url = 'freelancer:profile'
    
    def get(self, request, education_id):
        try:
            education = Education.objects.get(
                id=education_id,
                freelancer__user=request.user
            )
            education.delete()
            
            messages.success(request, 'Your education has been successfully deleted!')  
            return redirect(self.freelancer_profile_url)
        
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
        
class EditFreelancerLinksView(CustomLoginRequiredMixin, View):
    edit_links_template = 'freelancerprofile/editlinks.html'
    edit_links_url = 'freelancer:edit-links'
    freelancer_profile_url = 'freelancer:profile'
    
    def get(self, request):
        try:
            user = request.user
            freelancer = Freelancer.objects.get(user=user)
            return render(request, self.edit_links_template, {
                'freelancer': freelancer
            })
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
        
    def post(self, request):
        try:
            user = request.user
            freelancer = Freelancer.objects.get(user=user)
            
            portfolio_url = request.POST.get('portfolio_url', '').strip()
            github_url = request.POST.get('github_url', '').strip()
            linkedin_url = request.POST.get('linkedin_url', '').strip()
            
            context = {
                'freelancer': freelancer,
                'portfolio_url': portfolio_url,
                'github_url': github_url,
                'linkedin_url': linkedin_url,
            }
            
            valid, error_message = validate_urls(portfolio_url, github_url, linkedin_url)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.edit_links_template, context)
            
            freelancer.portfolio_link = portfolio_url
            freelancer.github_link = github_url
            freelancer.linkedin_link = linkedin_url
            freelancer.save()
            
            messages.success(request, 'Your links have been updated successfully!')
            return redirect(self.freelancer_profile_url)
            
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.edit_links_url)

class FreelancerPasswordChangeView(CustomLoginRequiredMixin, View):
    password_update_template = 'freelancerprofile/passwordupdate.html'
    password_update_url = 'freelancer:change-password'
    home_url = 'home:home'
    
    def get(self, request):
        try:
            return render(request, self.password_update_template)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)
        
    def post(self, request):
        try:
            user = request.user
            
            oldpassword = request.POST.get('old_password').strip()
            newpassword = request.POST.get('new_password1').strip()
            confirmpassword = request.POST.get('new_password2').strip()
            
            valid, error_message = validate_change_password_form(oldpassword, newpassword, confirmpassword, request)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.password_update_template)    
             
            user.set_password(newpassword)
            user.save()
            update_session_auth_hash(request, user)
            
            messages.success(request, 'Your password has been updated successfully!')
            return redirect(self.password_update_url)

        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.password_update_url)
            
