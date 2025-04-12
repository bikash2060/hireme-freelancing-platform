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
import os

class BaseFreelancerView(CustomLoginRequiredMixin, View):
    """Base view for freelancer profile with common properties"""
    profile_template = 'freelancerprofile/profile.html'
    home_url = 'home:home'
    freelancer_profile_url = 'freelancer:profile'

    def get_freelancer(self, request):
        """Helper method to get freelancer instance"""
        return Freelancer.objects.get(user=request.user)

class GetCitiesByCountryView(BaseFreelancerView):
    """Handle fetching cities by country"""
    def get(self, request, *args, **kwargs):
        try:
            country_id = request.GET.get('country_id')
            if not country_id:
                return JsonResponse({'cities': []})
            
            cities = City.objects.filter(country_id=country_id).order_by('name').values('id', 'name')
            return JsonResponse({'cities': list(cities)})
        except Exception as e:
            return JsonResponse({'cities': []})

class FreelancerProfileView(BaseFreelancerView):
    """Display freelancer profile information"""
    def get(self, request):
        try:
            freelancer = self.get_freelancer(request)
            freelancer_languages = FreelancerLanguage.objects.filter(freelancer=freelancer).select_related('language')
            
            # Get ordered work experiences
            experiences = WorkExperience.objects.filter(freelancer=freelancer)
            ongoing_experiences = experiences.filter(currently_working=True).order_by('-start_date')
            past_experiences = experiences.filter(currently_working=False).order_by(
                '-end_date' if WorkExperience._meta.get_field('end_date').null else 'end_date'
            )
            ordered_experiences = list(chain(ongoing_experiences, past_experiences))
            
            # Get ordered educations
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

class PersonalInfoView(BaseFreelancerView):
    """Handle freelancer personal information"""
    template_name = 'freelancerprofile/editpersonalinfo.html'
    edit_url = 'freelancer:edit-personal-info'

    def get(self, request):
        try:
            user = request.user
            freelancer = self.get_freelancer(request)
            all_countries = Country.objects.all().order_by('name')
            
            return render(request, self.template_name, {
                'freelancer': freelancer,
                'countries': all_countries,
                'current_country': user.country.id if user.country else None,
                'current_city': user.city.id if user.city else None,
            })
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)

    def post(self, request):
        try:
            user = request.user
            freelancer = self.get_freelancer(request)
            all_countries = Country.objects.all().order_by('name')
            
            # Get form data
            profile_image = request.FILES.get('profile_image')
            full_name = request.POST.get('full_name').strip()
            username = request.POST.get('username').strip().lower()
            phone_number = request.POST.get('phone_number').strip()
            city_id = request.POST.get('city')
            country_id = request.POST.get('country')
            bio = request.POST.get('bio').strip()
            
            # Prepare context for form re-rendering
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
            
            # Validate form data
            valid, error_message = ProfileValidator.validate_user_data(
                profile_image, full_name, username, phone_number, bio, city_id, country_id, request
            )
            if not valid:
                messages.error(request, error_message)
                return render(request, self.template_name, context)
            
            # Update country and city
            if country_id:
                try:
                    country = Country.objects.get(id=country_id)
                    user.country = country
                except Country.DoesNotExist:
                    messages.error(request, 'Selected country is not valid')
                    return render(request, self.template_name, context)
            
            if city_id:
                try:
                    city = City.objects.get(id=city_id)
                    user.city = city
                except City.DoesNotExist:
                    messages.error(request, 'Selected city is not valid')
                    return render(request, self.template_name, context)

            # Handle profile image
            if profile_image:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'profile_images'))
                filename = fs.save(profile_image.name, profile_image)
                user.profile_image = filename.split('/')[-1]
                
            # Update user fields
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
            return redirect(self.edit_url)

class DeleteProfileImageView(BaseFreelancerView):
    """Handle profile image deletion"""
    edit_url = 'freelancer:edit-personal-info'
    
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
            return redirect(self.edit_url)

class ProfessionalInfoView(BaseFreelancerView):
    """Handle freelancer professional information"""
    template_name = 'freelancerprofile/editprofessionalinfo.html'
    edit_url = 'freelancer:edit-professional-info'

    def get(self, request):
        try:
            freelancer = self.get_freelancer(request)
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

            return render(request, self.template_name, {
                'freelancer': freelancer,
                'skills': all_skills,
                'skills_select': selected_skills,
                'all_languages': all_languages,
                'language_proficiencies_list': language_proficiencies_list,
                'expertise_levels': Freelancer.ExpertiseLevel.choices,
                'availability_options': Freelancer.Availability.choices,
                'project_durations': Freelancer.ProjectDuration.choices,
                'communication_preferences': Freelancer.CommunicationPreference.choices,
            })
            
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
    
    def post(self, request):
        try: 
            freelancer = self.get_freelancer(request)
            all_skills = Skill.objects.all().order_by('name')
            all_languages = Language.objects.all()

            # Get form data
            years_of_experience = request.POST.get('years_of_experience')
            expertise_level = request.POST.get('expertise_level')
            availability = request.POST.get('availability')
            preferred_project_duration = request.POST.get('preferred_project_duration')
            communication_preference = request.POST.get('communication_preference')
            professional_title = request.POST.get('professional_title').strip()
            selected_skills = [int(skill_id) for skill_id in request.POST.getlist('skills')]

            # Process language proficiencies
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

            # Prepare context
            context = {
                'freelancer': freelancer,
                'skills': all_skills,
                'skills_select': selected_skills,
                'all_languages': all_languages,
                'language_proficiencies_list': language_proficiencies_list, 
                'years_of_experience': years_of_experience,
                'expertise_level': expertise_level,
                'availability': availability,
                'preferred_project_duration': preferred_project_duration,
                'professional_title': professional_title,
                'communication_preference': communication_preference,
                'expertise_levels': Freelancer.ExpertiseLevel.choices,
                'availability_options': Freelancer.Availability.choices,
                'project_durations': Freelancer.ProjectDuration.choices,
                'communication_preferences': Freelancer.CommunicationPreference.choices,
            }
            
            # Validate professional info
            valid, error_message = ProfessionalValidator.validate_professional_info(
                years_of_experience,
                expertise_level,
                availability,
                preferred_project_duration,
                professional_title,
                communication_preference,
                selected_skills, 
                language_proficiencies
            )
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.template_name, context)
                
            # Update freelancer fields
            freelancer.years_of_experience = years_of_experience if years_of_experience else 0
            freelancer.expertise_level = expertise_level
            freelancer.availability = availability
            freelancer.preferred_project_duration = preferred_project_duration
            freelancer.professional_title = professional_title
            freelancer.communication_preference = communication_preference
            
            freelancer.save()
            
            # Update skills
            freelancer.skills.clear()
            skills = Skill.objects.filter(id__in=selected_skills)
            freelancer.skills.add(*skills)
            
            # Update languages
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
                
            request.user.save()
            messages.success(request, "Your professional information has been updated successfully!")
            return redirect(self.freelancer_profile_url)
            
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.edit_url)

class ExperienceBaseView(BaseFreelancerView):
    """Base view for experience-related operations"""
    def get_common_data(self, request):
        """Helper method to get common data for experience views"""
        return {
            'skills': Skill.objects.all().order_by('name'),
            'countries': Country.objects.all().order_by('name'),
            'employment_types': WorkExperience.EmploymentType.choices
        }

class AddExperienceView(ExperienceBaseView):
    """Handle adding new work experience"""
    template_name = 'freelancerprofile/addexperience.html'
    add_url = 'freelancer:add-experience'

    def get(self, request):
        try:
            context = self.get_common_data(request)
            return render(request, self.template_name, context)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
    
    def post(self, request):
        try:
            freelancer = self.get_freelancer(request)
            
            # Get form data
            company_name = request.POST.get('company_name').strip()
            job_title = request.POST.get('job_title').strip()
            employment_type = request.POST.get('employment_type')
            start_date = request.POST.get('start_date')
            currently_working = request.POST.get('currently_working') == 'on'  
            end_date = request.POST.get('end_date') if not currently_working else None
            country_id = request.POST.get('country')
            city_id = request.POST.get('city')
            job_description = request.POST.get('job_description').strip()
            selected_skill_ids = [int(skill_id) for skill_id in request.POST.getlist('skills')]
            
            # Prepare form data for re-rendering
            form_data = {
                'company_name': company_name,
                'job_title': job_title,
                'employment_type': employment_type,
                'start_date': start_date,
                'currently_working': currently_working,
                'end_date': end_date,
                'job_description': job_description,
                **self.get_common_data(request),
                'current_country': int(country_id) if country_id else None,
                'current_city': int(city_id) if city_id else None,
                'skills_select': selected_skill_ids,
            }
            
            # Validate employment data
            valid, error_message = EmploymentValidator.validate_employment_data(
                company_name, job_title, employment_type, start_date,
                currently_working, end_date, country_id, city_id, selected_skill_ids
            )
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.template_name, form_data)
            
            # Create experience
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
            return redirect(self.add_url)

class EditExperienceView(ExperienceBaseView):
    """Handle editing work experience"""
    template_name = 'freelancerprofile/editexperience.html'
    edit_url = 'freelancer:edit-experience'

    def get(self, request, experience_id):
        try:
            experience = WorkExperience.objects.get(id=experience_id, freelancer__user=request.user)
            selected_skill_ids = list(experience.skills.values_list('id', flat=True))
            
            form_data = {
                'experience': experience,
                'current_country': experience.country.id if experience.country else None,
                'current_city': experience.city.id if experience.city else None,
                'skills_select': selected_skill_ids,
                **self.get_common_data(request),
            }
            return render(request, self.template_name, form_data)

        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
    
    def post(self, request, experience_id):
        try:
            freelancer = self.get_freelancer(request)
            experience = WorkExperience.objects.get(id=experience_id, freelancer__user=request.user)
            
            # Get form data
            company_name = request.POST.get('company_name')
            job_title = request.POST.get('job_title')
            employment_type = request.POST.get('employment_type')
            start_date = request.POST.get('start_date')
            currently_working = request.POST.get('currently_working') == 'on'
            end_date = request.POST.get('end_date') if not currently_working else None
            country_id = request.POST.get('country')
            city_id = request.POST.get('city')
            job_description = request.POST.get('job_description')
            selected_skill_ids = [int(skill_id) for skill_id in request.POST.getlist('skills')]
            
            # Prepare form data
            form_data = {
                'experience': experience,
                'company_name': company_name,
                'job_title': job_title,
                'employment_type': employment_type,
                'start_date': start_date,
                'currently_working': currently_working,
                'end_date': end_date,
                **self.get_common_data(request),
                'current_country': int(country_id) if country_id else None,
                'current_city': int(city_id) if city_id else None,
                'job_description': job_description,
                'skills_select': selected_skill_ids,
            }
            
            # Validate employment data
            valid, error_message = EmploymentValidator.validate_employment_data(
                company_name, job_title, employment_type, start_date,
                currently_working, end_date, country_id, city_id, selected_skill_ids
            )            
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.template_name, form_data)
            
            # Update experience
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
            return redirect(reverse(self.edit_url, kwargs={'experience_id': experience_id}))

class DeleteExperienceView(BaseFreelancerView):
    """Handle deleting work experience"""
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

class EducationBaseView(BaseFreelancerView):
    """Base view for education-related operations"""
    def get_education_context(self, education=None):
        """Helper method to get education context"""
        context = {
            'degree_choices': Education.DegreeType.choices  # Add degree choices to context
        }
        if education:
            context.update({
                'education': education,
                'institution': education.institution,
                'degree': education.degree,
                'gpa': education.gpa,
                'start_date': education.start_date.strftime('%Y-%m') if education.start_date else None,
                'currently_studying': education.currently_studying,
                'end_date': education.end_date.strftime('%Y-%m') if education.end_date else None,
            })
        return context

class AddEducationView(EducationBaseView):
    """Handle adding new education"""
    template_name = 'freelancerprofile/addeducation.html'
    add_url = 'freelancer:add-education'

    def get(self, request):
        try:
            context = self.get_education_context()  # Get base context with choices
            return render(request, self.template_name, context)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
        
    def post(self, request):
        try:
            freelancer = self.get_freelancer(request)
            
            # Get form data
            institution = request.POST.get('institution')
            degree = request.POST.get('degree')
            gpa = request.POST.get('gpa')
            start_date = request.POST.get('start_date')
            currently_studying = request.POST.get('currently_studying') == 'on'  
            end_date = request.POST.get('end_date') if not currently_studying else None
            
            # Prepare context
            context = self.get_education_context()
            context.update({
                'institution': institution,
                'degree': degree,
                'gpa': gpa,
                'start_date': start_date,
                'currently_studying': currently_studying,
                'end_date': end_date,
            })
            
            # Validate education data
            valid, error_message = EducationValidator.validate_education_data(
                institution, degree, start_date, currently_studying, end_date, gpa
            )
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.template_name, context)
            
            # Create education
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
            return redirect(self.add_url)

class EditEducationView(EducationBaseView):
    """Handle editing education"""
    template_name = 'freelancerprofile/editeducation.html'
    edit_url = 'freelancer:edit-education'

    def get(self, request, education_id):
        try:
            education = Education.objects.get(id=education_id, freelancer__user=request.user)
            context = self.get_education_context(education)  # This now includes degree_choices
            context['freelancer'] = self.get_freelancer(request)
            return render(request, self.template_name, context)
        except Education.DoesNotExist:
            messages.error(request, 'Education record not found.')
            return redirect(self.freelancer_profile_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
       
    def post(self, request, education_id):
        try:
            freelancer = self.get_freelancer(request)
            education = Education.objects.get(id=education_id, freelancer__user=request.user)
            
            # Get form data
            institution = request.POST.get('institution')
            degree = request.POST.get('degree')
            gpa = request.POST.get('gpa')
            start_date = request.POST.get('start_date')
            currently_studying = request.POST.get('currently_studying') == 'on'  
            end_date = request.POST.get('end_date') if not currently_studying else None
            
            # Prepare context with degree choices
            context = self.get_education_context(education)  # Get base context with choices
            context.update({
                'freelancer': freelancer,
                'institution': institution,
                'degree': degree,
                'gpa': gpa,
                'start_date': start_date,
                'currently_studying': currently_studying,
                'end_date': end_date,
            })
            
            # Validate education data
            valid, error_message = EducationValidator.validate_education_data(
                institution, degree, start_date, currently_studying, end_date, gpa
            )
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.template_name, context)
            
            # Update education
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
            
        except Education.DoesNotExist:
            messages.error(request, 'Education record not found.')
            return redirect(self.freelancer_profile_url)
        except Exception as e:
            print(f'Error updating education: {str(e)}')
            messages.error(request, 'Something went wrong while updating your education.')
            return redirect(reverse(self.edit_url, kwargs={'education_id': education_id}))

class DeleteEducationView(BaseFreelancerView):
    """Handle deleting education"""
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

class EditLinksView(BaseFreelancerView):
    """Handle editing freelancer links"""
    template_name = 'freelancerprofile/editlinks.html'
    edit_url = 'freelancer:edit-links'

    def get(self, request):
        try:
            freelancer = self.get_freelancer(request)
            return render(request, self.template_name, {
                'freelancer': freelancer
            })
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
        
    def post(self, request):
        try:
            freelancer = self.get_freelancer(request)
            
            # Get form data
            portfolio_url = request.POST.get('portfolio_url', '').strip()
            github_url = request.POST.get('github_url', '').strip()
            linkedin_url = request.POST.get('linkedin_url', '').strip()
            
            # Prepare context
            context = {
                'freelancer': freelancer,
                'portfolio_url': portfolio_url,
                'github_url': github_url,
                'linkedin_url': linkedin_url,
            }
            
            # Validate URLs
            valid, error_message = URLValidator.validate_urls(portfolio_url, github_url, linkedin_url)
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.template_name, context)
            
            # Update links
            freelancer.portfolio_link = portfolio_url
            freelancer.github_link = github_url
            freelancer.linkedin_link = linkedin_url
            freelancer.save()
            
            messages.success(request, 'Your links have been updated successfully!')
            return redirect(self.freelancer_profile_url)
            
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.edit_url)

class PasswordChangeView(BaseFreelancerView):
    """Handle password change"""
    template_name = 'freelancerprofile/passwordupdate.html'
    edit_url = 'freelancer:change-password'

    def get(self, request):
        try:
            return render(request, self.template_name)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)
        
    def post(self, request):
        try:
            # Get form data
            oldpassword = request.POST.get('old_password').strip()
            newpassword = request.POST.get('new_password1').strip()
            confirmpassword = request.POST.get('new_password2').strip()
            
            # Validate password change
            valid, error_message = PasswordValidator.validate_change_password_form(
                oldpassword, newpassword, confirmpassword, request
            )
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.template_name)    
             
            # Update password
            request.user.set_password(newpassword)
            request.user.save()
            update_session_auth_hash(request, request.user)
            
            messages.success(request, 'Your password has been updated successfully!')
            return redirect(self.edit_url)

        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.edit_url)