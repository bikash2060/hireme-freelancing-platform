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

class ClientBasicInfoView(CustomLoginRequiredMixin, View):
    profile_template = 'clientprofile/profile.html'
    home_url = 'home:home'

    def get(self, request):
        try:
            client = Client.objects.get(user=request.user)
            return render(request, self.profile_template, {
                'client': client
            })
    
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.home_url)            

class EditFreelancerPersonalInfoView(CustomLoginRequiredMixin, View):
    personal_details_template = 'clientprofile/editpersonalinfo.html'
    personal_details_url = 'client:edit-personal-info'
    client_profile_url = 'client:profile'

    def get(self, request):
        try:
            user = request.user
            client = Client.objects.get(user=request.user)
            all_countries = Country.objects.all().order_by('name')
            current_country = user.country.id if user.country else None
            current_city = user.city.id if user.city else None
            return render(request, self.personal_details_template, {
                'client': client,
                'countries': all_countries,
                'current_country': current_country,
                'current_city': current_city

            })
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.client_profile_url)

    def post(self, request):
        try:
            user = request.user
            client = Client.objects.get(user=request.user)
            all_countries = Country.objects.all().order_by('name')
            
            profile_image = request.FILES.get('profile_image')
            full_name = request.POST.get('full_name').strip()
            username = request.POST.get('username').strip().lower()
            phone_number = request.POST.get('phone_number').strip()
            bio = request.POST.get('bio').strip()
            city_id = request.POST.get('city')
            country_id = request.POST.get('country')
            
            form_data = {
                'client': client,
                'full_name': full_name if full_name else None,
                'username': username if username else None,
                'phone_number': phone_number if phone_number else None,
                'bio': bio if bio else None,
                'countries': all_countries,
                'current_city': int(city_id) if city_id else None,
                'current_country': int(country_id) if country_id else None,
                
            }
            
            valid, error_message = validate_user_data(profile_image, full_name, username, phone_number, city_id, country_id, bio, request)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.personal_details_template, form_data)
                
            if country_id:
                try:
                    country = Country.objects.get(id=country_id)
                    user.country = country
                except Country.DoesNotExist:
                    messages.error(request, 'Selected country is not valid')
                    return render(request, self.professional_info_template, form_data)
            
            if city_id:
                try:
                    city = City.objects.get(id=city_id)
                    user.city = city
                except City.DoesNotExist:
                    messages.error(request, 'Selected city is not valid')
                    return render(request, self.professional_info_template, form_data)

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
            return redirect(self.client_profile_url)
            
        except Exception as e:
            print('Exception:', e)
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.personal_details_url)

class DeleteProfileImageView(CustomLoginRequiredMixin, View):
    client_profile_url = 'client:profile'
    personal_details_url = 'client:edit-personal-info'
    
    def get(self, request):
        try:
            print('Deleting profile image...')
            user = request.user
            if user.profile_image:
                file_path = os.path.join(settings.MEDIA_ROOT, 'profile_images', str(user.profile_image.name))
                
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print('Profile image deleted successfully!')
            user.profile_image = None
            user.save()
            
            messages.success(request, 'Your profile image has been deleted successfully!')
            return redirect(self.client_profile_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
        
class ClientChangePasswordView(CustomLoginRequiredMixin, View):
    password_update_template = 'clientprofile/passwordupdate.html'
    password_update_url = 'client:change-password'
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