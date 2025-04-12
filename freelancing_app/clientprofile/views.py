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

class BaseClientView(CustomLoginRequiredMixin, View):
    """Base view for client profile with common properties"""
    profile_template = 'clientprofile/profile.html'
    home_url = 'home:home'
    client_profile_url = 'client:profile'

    def get_client(self, request):
        """Helper method to get client instance"""
        return Client.objects.get(user=request.user)

class GetCitiesByCountryView(BaseClientView):
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

class ClientProfileView(BaseClientView):
    """Display client profile information"""
    def get(self, request):
        try:
            client = self.get_client(request)
            return render(request, self.profile_template, {
                'client': client
            })
    
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.home_url)

class PersonalInfoView(BaseClientView):
    """Handle client personal information"""
    template_name = 'clientprofile/editpersonalinfo.html'
    edit_url = 'client:edit-personal-info'

    def get(self, request):
        try:
            user = request.user
            client = self.get_client(request)
            all_countries = Country.objects.all().order_by('name')
            
            return render(request, self.template_name, {
                'client': client,
                'countries': all_countries,
                'current_country': user.country.id if user.country else None,
                'current_city': user.city.id if user.city else None,
            })
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.client_profile_url)

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
            return redirect(self.client_profile_url)
            
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.edit_url)

class DeleteProfileImageView(BaseClientView):
    """Handle profile image deletion"""
    edit_url = 'client:edit-personal-info'
    
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
            return redirect(self.client_profile_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.edit_url)

class PasswordChangeView(BaseClientView):
    """Handle password change"""
    template_name = 'clientprofile/passwordupdate.html'
    edit_url = 'client:change-password'

    def get(self, request):
        try:
            return render(request, self.template_name)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.home_url)
        
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
                return render(request, self.template_name)    
             
            # Update password
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            
            messages.success(request, 'Your password has been updated successfully!')
            return redirect(self.edit_url)

        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.edit_url)