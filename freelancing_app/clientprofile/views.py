from django.shortcuts import render, redirect
from django.views import View
from accounts.models import User, Client
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .utils import validate_username, validate_personal_info, validate_profile_image

class UserBasicInfoView(View):
    rendered_template = 'clientprofile/profile.html'
    
    def get(self, request):
        client = Client.objects.get(user=request.user)  
        
        return render(request, self.rendered_template, {'client': client})

# Full Testing In Progress
class EditProfileImageView(View):
    rendered_template = 'clientprofile/editprofileimage.html'
    redirected_URL = 'client:edit-profile-image'

    def get(self, request):
        client = Client.objects.get(user=request.user)
        return render(request, self.rendered_template, {'client': client})

    def post(self, request):
        profile_image = request.FILES.get('profile_image')
        username = request.POST.get('username')

        if profile_image:
            valid, error_message = validate_profile_image(profile_image)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.rendered_template, {'last_username': username})
        
        if not username:
            messages.error(request, "Username cannot be empty.")
            return render(request, self.rendered_template, {'last_username': username})

        valid, error_message = validate_username(username)
        if not valid:
            messages.error(request, error_message)
            return render(request, self.rendered_template, {'last_username': username})

        if User.objects.filter(username=username).exclude(id=request.user.id).exists():
            messages.error(request, "Username already taken.")
            return render(request, self.rendered_template, {'last_username': username})

        try:
            user = request.user
            user.username = username

            if profile_image:
                fs = FileSystemStorage(location='media/profile_images')
                filename = fs.save(profile_image.name, profile_image)
                user.profile_image = filename.split('/')[-1]

            user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect(self.redirected_URL)
        except FileNotFoundError:
            messages.error(request, "There was an issue uploading the profile image. Please try again.")
        except Exception as e:
            print(f"Exception: {e}")
            messages.error(request, "Something went wrong. Please try again later.")

        return render(request, self.rendered_template, {'last_username': username})


#Full Testing In Progress
class EditPersonalInfoView(View):
    rendered_template = 'clientprofile/editpersonalinfo.html'
    redirected_URL = 'client:edit-personal-info'

    def get(self, request):
        client = Client.objects.get(user=request.user)
        return render(request, self.rendered_template, {'client': client})
    
    def post(self, request):
        user = request.user
        client = Client.objects.get(user=request.user)

        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        bio = request.POST.get('bio')

        form_data = {
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'phone_number': phone_number,
            'bio': bio
        }

        valid, error_message = validate_personal_info(first_name, middle_name, last_name, phone_number, bio)

        if not valid:
            messages.error(request, error_message)
            return render(request, self.rendered_template, {'form_data': form_data, 'client': client})

        if phone_number and User.objects.filter(phone_number=phone_number).exclude(id=request.user.id).exists():
            messages.error(request, 'This phone number is already registered.')
            return render(request, self.rendered_template, {'form_data': form_data, 'client': client})

        try:
            
            user.first_name = first_name
            user.middle_name = middle_name if middle_name else user.middle_name  
            user.last_name = last_name
            user.phone_number = phone_number
            user.save()

            client.bio = bio
            client.save()
            messages.success(request, 'Profile Updated Successfully.')
            return redirect(self.redirected_URL)
        except Exception as e:
            messages.error(request, "Unable to update your profile.")
            return render(request, self.rendered_template, {'client': client})

