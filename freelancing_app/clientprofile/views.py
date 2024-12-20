from django.shortcuts import render, redirect
from django.views import View
from accounts.models import User, Client
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .utils import validate_username, validate_personal_info

class UserBasicInfoView(View):
    
    def get(self, request):
        client = Client.objects.get(user=request.user)  
        
        return render(request, 'clientprofile/profile.html', {'client': client})

class EditProfileImageView(View):
    rendered_template = 'clientprofile/editprofileimage.html'
    
    def get(self, request):
        client = Client.objects.get(user=request.user)  
        return render(request, self.rendered_template, {'client': client})
      
    def post(self, request):
        if request.method == 'POST':
            username = request.POST.get('username')
            profile_image = request.FILES.get('profile_image')

            if not username:
                messages.error(request, "Username cannot be empty.")
                return render(request, self.rendered_template)

            valid, error_message = validate_username(username)
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.rendered_template)
            
            if User.objects.filter(username=username).exclude(id=request.user.id).exists():
                messages.error(request, "Username already taken.")
                return render(request, self.rendered_template)

            try:
                user = request.user
                user.username = username

                if profile_image:
                    fs = FileSystemStorage(location='media/profile_images')
                    filename = fs.save(profile_image.name, profile_image)
                    file_name_only = filename.split('/')[-1]
                    user.profile_image = file_name_only

                user.save()
                messages.success(request, "Profile Updated Successfully.")
                return render(request, self.rendered_template)
            except FileNotFoundError:
                messages.error(request, "There was an issue uploading the profile image. Please try again.")
            except Exception as e:
                print(f"Exception:{e}")
                messages.error(request, "Something went wrong. Please try again later.")

            return render(request, self.rendered_template)


class EditPersonalInfoView(View):
    
    rendered_template = 'clientprofile/editpersonalinfo.html'
    
    def get(self, request):
        client = Client.objects.get(user=request.user)
        return render(request, self.rendered_template, {'client': client})
    
    def post(self, request):
        client = Client.objects.get(user=request.user)
        
        first_name = request.POST.get('first_name')
        print(f"First Name: {first_name}")
        last_name = request.POST.get('last_name')
        print(f"Last Name: {last_name}")
        phone_number = request.POST.get('phone_number')
        print(f"Phone Number: {phone_number}")
        languages = request.POST.get('languages')
        print(f"Language: {languages}")
        bio = request.POST.get('bio')
        print(f"Bio: {bio}")
        
        valid, error_message = validate_personal_info(first_name, last_name, phone_number, languages)
            
        if not valid:
            messages.error(request, error_message)
            return render(request, self.rendered_template)
                
        if Client.objects.filter(phone_number=phone_number).exclude(client_ID=client.client_ID).exists():
            messages.error(request, 'This phone number is already registered.')
            return render(request, self.rendered_template, {'client': client})
        
        language_list = languages.split(',')
        language_list = [language.strip() for language in language_list]  
        
        client.user.first_name = first_name
        client.user.last_name = last_name
        client.phone_number = phone_number
        client.languages = ', '.join(language_list)  
        client.bio = bio
        
        try:
            client.user.save()  
            client.save()       
            messages.success(request, 'Profile Updated Successfully.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, self.rendered_template, {'client': client})
        
        return render(request, self.rendered_template, {'client': client})
