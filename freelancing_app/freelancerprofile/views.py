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
from datetime import datetime
from django.views import View
from itertools import chain
from .models import *
from .utils import *
import os

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseFreelancerView
# Description: Base class for freelancer views with common utilities
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class BaseFreelancerView(CustomLoginRequiredMixin, View):
    """
    Base class for freelancer-related views. Provides utility methods and constants.
    Restricts access to users with the 'freelancer' role.
    """
    PROFILE_TEMPLATE = 'freelancerprofile/profile.html'
    HOME_URL = 'home:home'
    PROFILE_URL = 'freelancer:profile'

    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the user has freelancer role before proceeding.
        """
        
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        
        if not hasattr(request.user, 'role') or request.user.role != 'freelancer':
            messages.error(request, "Access denied. You must be a freelancer to view this page.")
            return redirect(self.HOME_URL)
        return super().dispatch(request, *args, **kwargs)

    def get_freelancer(self, request):
        """
        Get freelancer instance for the logged-in user.
        """
        return Freelancer.objects.get(user=request.user)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: GetCitiesByCountryView
# Description: Returns city list JSON based on selected country ID
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class GetCitiesByCountryView(BaseFreelancerView):
    """
    - Handles fetching cities based on selected country ID
    - Returns list of city ID-name pairs as JSON
    """

    def get(self, request, *args, **kwargs):
        try:
            country_id = request.GET.get('country_id')
            if not country_id:
                return JsonResponse({'cities': []})

            cities = City.objects.filter(country_id=country_id).order_by('name').values('id', 'name')
            return JsonResponse({'cities': list(cities)})

        except Exception as e:
            print(f"[GetCitiesByCountryView Error]: {e}")
            return JsonResponse({'cities': []})

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: FreelancerProfileView
# Description: Displays the logged-in freelancer's profile, including personal info,
#              work experience, education, and languages.
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class FreelancerProfileView(BaseFreelancerView):
    """
    - Renders the freelancer profile page
    - Displays personal info, education, experiences, and languages
    """

    def get(self, request):
        try:
            freelancer = self.get_freelancer(request)

            # Languages
            freelancer_languages = FreelancerLanguage.objects.filter(
                freelancer=freelancer
            ).select_related('language')

            # Work Experience (ordered: ongoing first)
            experiences = WorkExperience.objects.filter(freelancer=freelancer)
            ongoing_experiences = experiences.filter(currently_working=True).order_by('-start_date')
            past_experiences = experiences.filter(currently_working=False).order_by(
                '-end_date' if WorkExperience._meta.get_field('end_date').null else 'end_date'
            )
            ordered_experiences = list(chain(ongoing_experiences, past_experiences))

            # Education (ordered: ongoing first)
            educations = Education.objects.filter(freelancer=freelancer)
            ongoing_educations = educations.filter(currently_studying=True).order_by('-start_date')
            past_educations = educations.filter(currently_studying=False).order_by(
                '-end_date' if Education._meta.get_field('end_date').null else 'end_date'
            )
            ordered_educations = list(chain(ongoing_educations, past_educations))

            # Render profile
            return render(request, self.PROFILE_TEMPLATE, {
                'freelancer': freelancer,
                'freelancer_languages': freelancer_languages,
                'experiences': ordered_experiences,
                'educations': ordered_educations,
            })

        except Exception as e:
            print(f"[FreelancerProfileView Error]: {e}")
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.HOME_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: PersonalInfoView
# Description: Allows freelancers to view and update their personal information
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class PersonalInfoView(BaseFreelancerView):
    """
    - Renders and processes the freelancer's personal information form
    - Allows updating name, username, bio, country, city, phone, and profile image
    """
    TEMPLATE_NAME = 'freelancerprofile/editpersonalinfo.html'
    EDIT_URL = 'freelancer:edit-personal-info'

    def get(self, request):
        try:
            user = request.user
            freelancer = self.get_freelancer(request)
            countries = Country.objects.all().order_by('name')

            return render(request, self.TEMPLATE_NAME, {
                'freelancer': freelancer,
                'countries': countries,
                'current_country': user.country.id if user.country else None,
                'current_city': user.city.id if user.city else None,
            })
            
        except Exception as e:
            print(f"[PersonalInfoView GET Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.PROFILE_URL)

    def post(self, request):

            user = request.user
            freelancer = self.get_freelancer(request)
            countries = Country.objects.all().order_by('name')

            # Extract form data
            profile_image = request.FILES.get('profile_image')
            full_name = request.POST.get('full_name', '').strip()
            username = request.POST.get('username', '').strip().lower()
            phone_number = request.POST.get('phone_number', '').strip()
            city_id = request.POST.get('city')
            country_id = request.POST.get('country')
            bio = request.POST.get('bio', '').strip()

            context = {
                'freelancer': freelancer,
                'full_name': full_name,
                'username': username,
                'phone_number': phone_number,
                'bio': bio,
                'countries': countries,
                'current_country': int(country_id) if country_id else None,
                'current_city': int(city_id) if city_id else None,
            }

            # Validate input
            valid, error_message = ProfileValidator.validate_user_data(
                profile_image, full_name, username, phone_number, bio, city_id, country_id, request
            )
            if not valid:
                messages.error(request, error_message)
                return render(request, self.TEMPLATE_NAME, context)

            # Update country
            if country_id:
                try:
                    user.country = Country.objects.get(id=country_id)
                except Country.DoesNotExist:
                    messages.error(request, 'Selected country is not valid.')
                    return render(request, self.TEMPLATE_NAME, context)

            # Update city
            if city_id:
                try:
                    user.city = City.objects.get(id=city_id)
                except City.DoesNotExist:
                    messages.error(request, 'Selected city is not valid.')
                    return render(request, self.TEMPLATE_NAME, context)

            # Handle profile image
            if profile_image:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'profile_images'))
                filename = fs.save(profile_image.name, profile_image)
                user.profile_image = filename.split('/')[-1]

            # Save user data
            user.full_name = full_name
            user.username = username
            user.phone_number = phone_number
            user.bio = bio
            user.save()

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect(self.PROFILE_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: DeleteProfileImageView
# Description: Deletes the freelancer's profile image from the server and database
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class DeleteProfileImageView(BaseFreelancerView):
    """
    - Deletes the freelancer's profile image file from disk
    - Sets the profile image field to None
    """
    EDIT_URL = 'freelancer:edit-personal-info'

    def get(self, request):
        try:
            user = request.user

            # Delete image from storage if exists
            if user.profile_image:
                image_path = os.path.join(settings.MEDIA_ROOT, 'profile_images', str(user.profile_image))
                if os.path.isfile(image_path):
                    os.remove(image_path)

            user.profile_image = None
            user.save()

            messages.success(request, 'Your profile image has been deleted successfully!')
            return redirect(self.PROFILE_URL)

        except Exception as e:
            print(f"[DeleteProfileImageView Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.EDIT_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ProfessionalInfoView
# Description: Allows freelancers to view and update their professional info
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class ProfessionalInfoView(BaseFreelancerView):
    """
    - Displays and updates freelancer's professional information
    - Includes expertise level, availability, project preferences, skills, languages
    """
    TEMPLATE_NAME = 'freelancerprofile/editprofessionalinfo.html'
    EDIT_URL = 'freelancer:edit-professional-info'

    def get(self, request):
        try:
            freelancer = self.get_freelancer(request)
            all_skills = Skill.objects.all().order_by('name')
            selected_skills = freelancer.skills.values_list('id', flat=True)
            all_languages = Language.objects.all()
            
            # Skill-level mapping
            selected_skill_levels = {
                fs.skill_id: fs.level
                for fs in FreelancerSkill.objects.filter(freelancer=freelancer)
            }

            # Load language proficiencies
            language_proficiencies = []
            for language in all_languages:
                proficiency = FreelancerLanguage.objects.filter(
                    freelancer=freelancer,
                    language=language
                ).values_list('proficiency', flat=True).first()

                language_proficiencies.append({
                    'code': language.code,
                    'name': language.name,
                    'proficiency': proficiency or None
                })

            return render(request, self.TEMPLATE_NAME, {
                'freelancer': freelancer,
                'skills': all_skills,
                'skills_select': selected_skills,
                'skill_levels_map': selected_skill_levels,
                'all_languages': all_languages,
                'language_proficiencies_list': language_proficiencies,
                'expertise_levels': Freelancer.ExpertiseLevel.choices,
                'availability_options': Freelancer.Availability.choices,
                'project_durations': Freelancer.ProjectDuration.choices,
                'communication_preferences': Freelancer.CommunicationPreference.choices,
                'freelancer_skill_levels': FreelancerSkill.SkillLevel.choices,
            })

        except Exception as e:
            print(f"[ProfessionalInfoView GET Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.PROFILE_URL)

    def post(self, request):
        try:
            freelancer = self.get_freelancer(request)
            all_skills = Skill.objects.all().order_by('name')
            all_languages = Language.objects.all()

            # Extract form data
            years_of_experience = request.POST.get('years_of_experience')
            expertise_level = request.POST.get('expertise_level')
            availability = request.POST.get('availability')
            project_duration = request.POST.get('preferred_project_duration')
            communication_pref = request.POST.get('communication_preference')
            professional_title = request.POST.get('professional_title', '').strip()
            selected_skill_ids = [int(sid) for sid in request.POST.getlist('skills')]
            
            skill_levels_map = {
                int(skill_id): request.POST.get(f'skill_level_{skill_id}', FreelancerSkill.SkillLevel.INTERMEDIATE)
                for skill_id in selected_skill_ids
            }

            # Parse language proficiencies
            language_proficiencies = {}
            language_proficiencies_list = []
            for language in all_languages:
                code = language.code
                value = request.POST.get(f'{code}_proficiency')
                if value:
                    language_proficiencies[code] = int(value)

                language_proficiencies_list.append({
                    'code': code,
                    'name': language.name,
                    'proficiency': int(value) if value else None
                })

            # Prepare context for re-rendering
            context = {
                'freelancer': freelancer,
                'skills': all_skills,
                'skills_select': selected_skill_ids,
                'skill_levels_map': skill_levels_map,
                'all_languages': all_languages,
                'language_proficiencies_list': language_proficiencies_list,
                'years_of_experience': years_of_experience,
                'expertise_level': expertise_level,
                'availability': availability,
                'preferred_project_duration': project_duration,
                'professional_title': professional_title,
                'communication_preference': communication_pref,
                'expertise_levels': Freelancer.ExpertiseLevel.choices,
                'availability_options': Freelancer.Availability.choices,
                'project_durations': Freelancer.ProjectDuration.choices,
                'communication_preferences': Freelancer.CommunicationPreference.choices,
                'freelancer_skill_levels': FreelancerSkill.SkillLevel.choices,
            }

            # Validate input
            valid, error_message = ProfessionalValidator.validate_professional_info(
                years_of_experience,
                expertise_level,
                availability,
                project_duration,
                professional_title,
                communication_pref,
                selected_skill_ids,
                language_proficiencies
            )

            if not valid:
                messages.error(request, error_message)
                return render(request, self.TEMPLATE_NAME, context)

            # Update freelancer model
            freelancer.years_of_experience = years_of_experience or 0
            freelancer.expertise_level = expertise_level
            freelancer.availability = availability
            freelancer.preferred_project_duration = project_duration
            freelancer.communication_preference = communication_pref
            freelancer.professional_title = professional_title
            freelancer.save()

            # Update skills
            freelancer.skills.clear()
            for skill_id in selected_skill_ids:
                skill = Skill.objects.get(id=skill_id)
                level = request.POST.get(f'skill_level_{skill_id}', FreelancerSkill.SkillLevel.INTERMEDIATE)
                FreelancerSkill.objects.create(
                    freelancer=freelancer,
                    skill=skill,
                    level=level
                )

            # Update language proficiencies
            FreelancerLanguage.objects.filter(freelancer=freelancer).delete()
            for code, proficiency in language_proficiencies.items():
                try:
                    lang = Language.objects.get(code=code)
                    FreelancerLanguage.objects.create(
                        freelancer=freelancer,
                        language=lang,
                        proficiency=proficiency
                    )
                except Language.DoesNotExist:
                    continue

            messages.success(request, 'Your professional information has been updated successfully!')
            return redirect(self.PROFILE_URL)

        except Exception as e:
            print(f"[ProfessionalInfoView POST Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.EDIT_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: ExperienceBaseView
# Description: Base class providing common data for experience views
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class ExperienceBaseView(BaseFreelancerView):
    """
    Base view for experience-related views. Provides commonly used dropdown data.
    """

    def get_common_data(self, request):
        return {
            'skills': Skill.objects.all().order_by('name'),
            'countries': Country.objects.all().order_by('name'),
            'employment_types': WorkExperience.EmploymentType.choices
        }

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: AddExperienceView
# Description: Handles the creation of new work experience for freelancers
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class AddExperienceView(ExperienceBaseView):
    """
    - Displays and processes the add experience form
    - Validates and saves new WorkExperience entries
    """
    TEMPLATE_NAME = 'freelancerprofile/addexperience.html'
    ADD_URL = 'freelancer:add-experience'

    def get(self, request):
        try:
            return render(request, self.TEMPLATE_NAME, self.get_common_data(request))
        except Exception as e:
            print(f"[AddExperienceView GET Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.PROFILE_URL)

    def post(self, request):
        try:
            freelancer = self.get_freelancer(request)
            form_data = self._extract_form_data(request)
            context = {**form_data, **self.get_common_data(request)}

            valid, error = EmploymentValidator.validate_employment_data(**form_data)
            if not valid:
                messages.error(request, error)
                return render(request, self.TEMPLATE_NAME, context)

            experience = self._create_experience(freelancer, form_data)
            experience.skills.set(form_data['selected_skill_ids'])

            messages.success(request, 'Your work experience has been successfully added!')
            return redirect(self.PROFILE_URL)

        except Exception as e:
            print(f"[AddExperienceView POST Error]: {e}")
            messages.error(request, 'Something went wrong while saving your experience.')
            return redirect(self.ADD_URL)

    def _extract_form_data(self, request):
        return {
            'company_name': request.POST.get('company_name', '').strip(),
            'job_title': request.POST.get('job_title', '').strip(),
            'employment_type': request.POST.get('employment_type'),
            'start_date': request.POST.get('start_date'),
            'currently_working': request.POST.get('currently_working') == 'on',
            'end_date': request.POST.get('end_date'),
            'country_id': request.POST.get('country'),
            'city_id': request.POST.get('city'),
            'job_description': request.POST.get('job_description', '').strip(),
            'selected_skill_ids': [int(id) for id in request.POST.getlist('skills')],
        }

    def _create_experience(self, freelancer, data):
        start = datetime.strptime(data['start_date'], '%Y-%m').date()
        end = datetime.strptime(data['end_date'], '%Y-%m').date() if data['end_date'] else None
        country = Country.objects.get(id=data['country_id']) if data['country_id'] else None
        city = City.objects.get(id=data['city_id']) if data['city_id'] else None

        return WorkExperience.objects.create(
            freelancer=freelancer,
            company_name=data['company_name'],
            job_title=data['job_title'],
            employment_type=data['employment_type'],
            start_date=start,
            end_date=end,
            currently_working=data['currently_working'],
            country=country,
            city=city,
            description=data['job_description'],
        )

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: EditExperienceView
# Description: Allows freelancers to update their previous work experiences
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class EditExperienceView(ExperienceBaseView):
    """
    - Edits existing experience record
    - Prepopulates form with existing values
    """
    TEMPLATE_NAME = 'freelancerprofile/editexperience.html'
    EDIT_URL = 'freelancer:edit-experience'

    def get(self, request, experience_id):
        try:
            experience = WorkExperience.objects.get(id=experience_id, freelancer__user=request.user)
            selected_skill_ids = list(experience.skills.values_list('id', flat=True))

            context = {
                'experience': experience,
                'current_country': experience.country.id if experience.country else None,
                'current_city': experience.city.id if experience.city else None,
                'skills_select': selected_skill_ids,
                **self.get_common_data(request),
            }
            return render(request, self.TEMPLATE_NAME, context)

        except Exception as e:
            print(f"[EditExperienceView GET Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.PROFILE_URL)

    def post(self, request, experience_id):
        try:
            experience = WorkExperience.objects.get(id=experience_id, freelancer__user=request.user)
            form_data = AddExperienceView()._extract_form_data(request)
            context = {
                'experience': experience,
                'skills_select': form_data['selected_skill_ids'],
                'current_country': int(form_data['country_id']) if form_data['country_id'] else None,
                'current_city': int(form_data['city_id']) if form_data['city_id'] else None,
                **self.get_common_data(request),
                **form_data
            }

            valid, error = EmploymentValidator.validate_employment_data(**form_data)
            if not valid:
                messages.error(request, error)
                return render(request, self.TEMPLATE_NAME, context)

            # Update experience directly
            experience.company_name = form_data['company_name']
            experience.job_title = form_data['job_title']
            experience.employment_type = form_data['employment_type']
            experience.start_date = datetime.strptime(form_data['start_date'], '%Y-%m').date()
            experience.end_date = datetime.strptime(form_data['end_date'], '%Y-%m').date() if form_data['end_date'] else None
            experience.currently_working = form_data['currently_working']
            experience.country = Country.objects.get(id=form_data['country_id']) if form_data['country_id'] else None
            experience.city = City.objects.get(id=form_data['city_id']) if form_data['city_id'] else None
            experience.description = form_data['job_description']
            experience.save()
            
            # Update skills
            experience.skills.set(form_data['selected_skill_ids'])

            messages.success(request, 'Your work experience has been successfully updated!')
            return redirect(self.PROFILE_URL)

        except Exception as e:
            print(f"[EditExperienceView POST Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(reverse(self.EDIT_URL, kwargs={'experience_id': experience_id}))

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: DeleteExperienceView
# Description: Deletes a freelancer's work experience
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class DeleteExperienceView(BaseFreelancerView):
    """
    - Deletes a specific work experience record
    - Only accessible to the owner freelancer
    """

    def get(self, request, experience_id):
        try:
            experience = WorkExperience.objects.get(id=experience_id, freelancer__user=request.user)
            experience.delete()

            messages.success(request, 'Your work experience has been successfully deleted!')
            return redirect(self.PROFILE_URL)

        except Exception as e:
            print(f"[DeleteExperienceView Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.PROFILE_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: EducationBaseView
# Description: Base class for education-related views with shared context
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class EducationBaseView(BaseFreelancerView):
    """
    Base view for education-related operations. Provides reusable context.
    """

    def get_education_context(self, education=None):
        context = {
            'degree_choices': Education.DegreeType.choices
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

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: AddEducationView
# Description: Handles the creation of new education records
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class AddEducationView(EducationBaseView):
    """
    - Displays and processes form for adding education
    """
    TEMPLATE_NAME = 'freelancerprofile/addeducation.html'
    ADD_URL = 'freelancer:add-education'

    def get(self, request):
        try:
            context = self.get_education_context()
            return render(request, self.TEMPLATE_NAME, context)
        except Exception as e:
            print(f"[AddEducationView GET Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.PROFILE_URL)

    def post(self, request):
        try:
            freelancer = self.get_freelancer(request)
            form_data = self._extract_form_data(request)
            context = {**form_data, **self.get_education_context()}

            valid, error = EducationValidator.validate_education_data(**form_data)
            if not valid:
                messages.error(request, error)
                return render(request, self.TEMPLATE_NAME, context)

            self._create_education(freelancer, form_data)
            messages.success(request, 'Your education has been successfully added!')
            return redirect(self.PROFILE_URL)

        except Exception as e:
            print(f"[AddEducationView POST Error]: {e}")
            messages.error(request, 'Something went wrong while saving your education.')
            return redirect(self.ADD_URL)

    def _extract_form_data(self, request):
        return {
            'institution': request.POST.get('institution'),
            'degree': request.POST.get('degree'),
            'gpa': request.POST.get('gpa'),
            'start_date': request.POST.get('start_date'),
            'currently_studying': request.POST.get('currently_studying') == 'on',
            'end_date': request.POST.get('end_date')
        }

    def _create_education(self, freelancer, data):
        start = datetime.strptime(data['start_date'], '%Y-%m').date()
        end = datetime.strptime(data['end_date'], '%Y-%m').date() if data['end_date'] else None

        Education.objects.create(
            freelancer=freelancer,
            institution=data['institution'],
            degree=data['degree'],
            gpa=float(data['gpa']) if data['gpa'] else None,
            start_date=start,
            end_date=end,
            currently_studying=data['currently_studying'],
        )

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: EditEducationView
# Description: Allows editing of a freelancer's education record
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class EditEducationView(EducationBaseView):
    """
    - Displays and processes form for editing education entries
    """
    TEMPLATE_NAME = 'freelancerprofile/editeducation.html'
    EDIT_URL = 'freelancer:edit-education'

    def get(self, request, education_id):
        try:
            education = Education.objects.get(id=education_id, freelancer__user=request.user)
            context = self.get_education_context(education)
            context['freelancer'] = self.get_freelancer(request)
            return render(request, self.TEMPLATE_NAME, context)

        except Education.DoesNotExist:
            messages.error(request, 'Education record not found.')
            return redirect(self.PROFILE_URL)
        except Exception as e:
            print(f"[EditEducationView GET Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.PROFILE_URL)

    def post(self, request, education_id):
        try:
            education = Education.objects.get(id=education_id, freelancer__user=request.user)
            freelancer = self.get_freelancer(request)
            form_data = AddEducationView()._extract_form_data(request)
            context = {**form_data, **self.get_education_context(education), 'freelancer': freelancer}

            valid, error = EducationValidator.validate_education_data(**form_data)
            if not valid:
                messages.error(request, error)
                return render(request, self.TEMPLATE_NAME, context)

            self._update_education(education, form_data)
            messages.success(request, 'Your education has been successfully updated!')
            return redirect(self.PROFILE_URL)

        except Education.DoesNotExist:
            messages.error(request, 'Education record not found.')
            return redirect(self.PROFILE_URL)
        except Exception as e:
            print(f"[EditEducationView POST Error]: {e}")
            messages.error(request, 'Something went wrong while updating your education.')
            return redirect(reverse(self.EDIT_URL, kwargs={'education_id': education_id}))

    def _update_education(self, education, data):
        education.institution = data['institution']
        education.degree = data['degree']
        education.gpa = float(data['gpa']) if data['gpa'] else None
        education.start_date = datetime.strptime(data['start_date'], '%Y-%m').date()
        education.end_date = datetime.strptime(data['end_date'], '%Y-%m').date() if data['end_date'] else None
        education.currently_studying = data['currently_studying']
        education.save()

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: DeleteEducationView
# Description: Deletes a freelancer's education record
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class DeleteEducationView(BaseFreelancerView):
    """
    - Deletes the specified education record for the freelancer
    """

    def get(self, request, education_id):
        try:
            education = Education.objects.get(id=education_id, freelancer__user=request.user)
            education.delete()

            messages.success(request, 'Your education has been successfully deleted!')
            return redirect(self.PROFILE_URL)

        except Exception as e:
            print(f"[DeleteEducationView Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.PROFILE_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: EditLinksView
# Description: Allows freelancers to update their external links (portfolio, GitHub, LinkedIn)
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class EditLinksView(BaseFreelancerView):
    """
    - Displays and updates freelancer's external profile links
    - Validates URL format before saving
    """
    TEMPLATE_NAME = 'freelancerprofile/editlinks.html'
    EDIT_URL = 'freelancer:edit-links'

    def get(self, request):
        try:
            freelancer = self.get_freelancer(request)
            return render(request, self.TEMPLATE_NAME, {
                'freelancer': freelancer
            })
        except Exception as e:
            print(f"[EditLinksView GET Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.PROFILE_URL)

    def post(self, request):
        try:
            freelancer = self.get_freelancer(request)

            # Extract form data
            portfolio_url = request.POST.get('portfolio_url', '').strip()
            github_url = request.POST.get('github_url', '').strip()
            linkedin_url = request.POST.get('linkedin_url', '').strip()

            context = {
                'freelancer': freelancer,
                'portfolio_url': portfolio_url,
                'github_url': github_url,
                'linkedin_url': linkedin_url,
            }

            # Validate URLs
            valid, error = URLValidator.validate_urls(portfolio_url, github_url, linkedin_url)
            if not valid:
                messages.error(request, error)
                return render(request, self.TEMPLATE_NAME, context)

            # Save to model
            freelancer.portfolio_link = portfolio_url
            freelancer.github_link = github_url
            freelancer.linkedin_link = linkedin_url
            freelancer.save()

            messages.success(request, 'Your links have been updated successfully!')
            return redirect(self.PROFILE_URL)

        except Exception as e:
            print(f"[EditLinksView POST Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.EDIT_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: PasswordChangeView
# Description: Enables freelancers to securely change their account password
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class PasswordChangeView(BaseFreelancerView):
    """
    - Allows logged-in freelancers to change their password
    - Validates current and new password inputs
    """
    TEMPLATE_NAME = 'freelancerprofile/passwordupdate.html'
    EDIT_URL = 'freelancer:change-password'

    def get(self, request):
        try:
            return render(request, self.TEMPLATE_NAME)
        except Exception as e:
            print(f"[PasswordChangeView GET Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.HOME_URL)

    def post(self, request):
        try:
            # Get form input
            old_password = request.POST.get('old_password', '').strip()
            new_password = request.POST.get('new_password1', '').strip()
            confirm_password = request.POST.get('new_password2', '').strip()

            # Validate input
            valid, error = PasswordValidator.validate_change_password_form(
                old_password, new_password, confirm_password, request
            )
            if not valid:
                messages.error(request, error)
                return render(request, self.TEMPLATE_NAME)

            # Update password
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)

            messages.success(request, 'Your password has been updated successfully!')
            return redirect(self.EDIT_URL)

        except Exception as e:
            print(f"[PasswordChangeView POST Error]: {e}")
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.EDIT_URL)
