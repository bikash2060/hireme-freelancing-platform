from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import FileSystemStorage
from accounts.mixins import CustomLoginRequiredMixin
from django.shortcuts import render, redirect
from accounts.models import City, Country
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.views import View
from .models import Client
from .utils import *
import os

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: BaseClientView
# Description: Base class for client-related views with utility methods
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class BaseClientView(CustomLoginRequiredMixin, View):
    """
    Base class for client-related views. Provides utility methods and constants.
    Restricts access to users with the 'client' role.
    """
    PROFILE_TEMPLATE = 'clientprofile/profile.html'
    HOME_URL = 'home:home'
    PROFILE_URL = 'client:profile'

    def dispatch(self, request, *args, **kwargs):
        """
        Ensure the user has client role before proceeding.
        """
        
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        
        if not hasattr(request.user, 'role') or request.user.role != 'client':
            messages.error(request, "Access denied. You must be a client to view this page.")
            return redirect(self.HOME_URL)
        return super().dispatch(request, *args, **kwargs)

    def get_client(self, request):
        """
        Get client instance for the logged-in user.
        """
        return Client.objects.get(user=request.user)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: GetCitiesByCountryView
# Description: Returns city list JSON based on selected country ID
# Tested On: 2025-04-23
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class GetCitiesByCountryView(BaseClientView):
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
# View Name: ClientProfileView
# Description: Displays the logged-in client's profile information
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class ClientProfileView(BaseClientView):
    """
    - Displays the logged-in client's profile information
    - Includes personal info, location, and profile image
    """

    def get(self, request):
        try:
            client = self.get_client(request)
            return render(request, self.PROFILE_TEMPLATE, {
                'client': client
            })
    
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.HOME_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: PersonalInfoView
# Description: Handles the client's personal information form
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class PersonalInfoView(BaseClientView):
    """
    - Renders and processes the client's personal information form
    - Allows updating name, username, bio, country, city, phone, and profile image
    """
    TEMPLATE_NAME = 'clientprofile/editpersonalinfo.html'
    EDIT_URL = 'client:edit-personal-info'

    def get(self, request):
        try:
            user = request.user
            client = self.get_client(request)
            all_countries = Country.objects.all().order_by('name')
            
            return render(request, self.TEMPLATE_NAME, {
                'client': client,
                'countries': all_countries,
                'current_country': user.country.id if user.country else None,
                'current_city': user.city.id if user.city else None,
            })
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.PROFILE_URL)

    def post(self, request):
        try:
            user = request.user
            client = self.get_client(request)
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
                'client': client,
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
                return render(request, self.TEMPLATE_NAME, context)
            
            # Update country and city
            if country_id:
                try:
                    country = Country.objects.get(id=country_id)
                    user.country = country
                except Country.DoesNotExist:
                    messages.error(request, 'Selected country is not valid')
                    return render(request, self.TEMPLATE_NAME, context)
            
            if city_id:
                try:
                    city = City.objects.get(id=city_id)
                    user.city = city
                except City.DoesNotExist:
                    messages.error(request, 'Selected city is not valid')
                    return render(request, self.TEMPLATE_NAME, context)

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
            return redirect(self.PROFILE_URL)
            
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.EDIT_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: DeleteProfileImageView
# Description: Deletes the client's profile image from the server and database
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class DeleteProfileImageView(BaseClientView):
    """
    - Deletes the client's profile image file from disk
    - Sets the profile image field to None
    """
    EDIT_URL = 'client:edit-personal-info'
    
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
            return redirect(self.PROFILE_URL)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.EDIT_URL)

# ------------------------------------------------------
# ✅ [TESTED & COMPLETED]
# View Name: PasswordChangeView
# Description: Enables clients to securely change their account password
# Tested On: 2025-04-25
# Status: Working as expected
# Code Refractor Status: Completed
# ------------------------------------------------------
class PasswordChangeView(BaseClientView):
    """
    - Enables clients to securely change their account password
    - Validates current and new password inputs
    """
    TEMPLATE_NAME = 'clientprofile/passwordupdate.html'
    EDIT_URL = 'client:change-password'

    def get(self, request):
        try:
            return render(request, self.TEMPLATE_NAME)
        except Exception as e: 
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.HOME_URL)
        
    def post(self, request):
        try:
            # Get form data
            old_password = request.POST.get('old_password').strip()
            new_password = request.POST.get('new_password1').strip()
            confirm_password = request.POST.get('new_password2').strip()
            
            # Validate password change
            valid, error_message = PasswordValidator.validate_change_password_form(
                old_password, new_password, confirm_password, request
            )
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.TEMPLATE_NAME)    
             
            # Update password
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            
            messages.success(request, 'Your password has been updated successfully!')
            return redirect(self.EDIT_URL)

        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.EDIT_URL)