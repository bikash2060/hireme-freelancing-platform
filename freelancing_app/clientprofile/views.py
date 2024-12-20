from django.shortcuts import render, redirect
from django.views import View
from accounts.models import User, Client
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.core.exceptions import ValidationError

class UserBasicInfoView(View):
    
    def get(self, request):
        client = Client.objects.get(user=request.user)  
        
        return render(request, 'clientprofile/basic-info.html', {'client': client})

class EditProfileImageView(View):
    def post(self, request):
        if request.method == 'POST':
            username = request.POST.get('username')
            profile_image = request.FILES.get('profile_image')

            if not username:
                messages.error(request, "Username cannot be empty.")
                return render(request, 'clientprofile/basic-info.html')

            if User.objects.filter(username=username).exclude(id=request.user.id).exists():
                messages.error(request, "Username already taken.")
                return render(request, 'clientprofile/basic-info.html')

            try:
                user = request.user
                user.username = username

                if profile_image:
                    fs = FileSystemStorage(location='media/profile_images')  
                    filename = fs.save(profile_image.name, profile_image)  
                    file_name_only = filename.split('/')[-1]  
                    user.profile_image = file_name_only  
                user.save()

                messages.success(request, "Profile Updated Successfully!")
                return redirect('client:profile')  

            except ValidationError as e:
                messages.error(request, f"Error: {e}")
                return render(request, 'clientprofile/basic-info.html')
