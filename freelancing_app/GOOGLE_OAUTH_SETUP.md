# Google OAuth2 Setup for Freelancing App

## Prerequisites
- Google Cloud Console account
- Django project with django-allauth installed

## Configuration Steps

### 1. Create Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" and select "OAuth client ID"
5. Choose "Web application" as the application type
6. Set the following:
   - Name: "Freelancing App" (or your preferred name)
   - Authorized JavaScript origins: 
     - `http://localhost:8000` (for development)
     - Your production domain (for production)
   - Authorized redirect URIs: 
     - `http://localhost:8000/accounts/google/login/callback/`
     - `http://localhost:8000/accounts/google/login/complete/`
     - Your production domain equivalents
7. Click "Create" and note down your "Client ID" and "Client Secret"

### 2. Configure Django Settings

1. Ensure django-allauth is installed: `pip install django-allauth`
2. Configure settings.py with the following:
   ```python
   INSTALLED_APPS = [
       # ...
       'django.contrib.sites',
       'allauth',
       'allauth.account',
       'allauth.socialaccount',
       'allauth.socialaccount.providers.google',
   ]
   
   MIDDLEWARE = [
       # ...
       'allauth.account.middleware.AccountMiddleware',
   ]
   
   AUTHENTICATION_BACKENDS = [
       # ...
       'django.contrib.auth.backends.ModelBackend',
       'allauth.account.auth_backends.AuthenticationBackend',
   ]
   
   SITE_ID = 1
   
   SOCIALACCOUNT_PROVIDERS = {
       'google': {
           'SCOPE': ['email', 'profile'],
           'AUTH_PARAMS': {'access_type': 'online'},
           'OAUTH_PKCE_ENABLED': True,
       }
   }
   
   SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'
   SOCIALACCOUNT_AUTO_SIGNUP = False
   ```

### 3. Configure Django Admin

1. Run the development server: `python manage.py runserver`
2. Access the admin site: `http://localhost:8000/admin/`
3. Navigate to "Sites" and update the default site:
   - Domain name: `localhost:8000` (for development) or your actual domain
   - Display name: "Freelancing App" or your site name
4. Add a new Social Application:
   - Provider: Select "Google"
   - Name: "Google"
   - Client ID: Your Google OAuth Client ID
   - Secret key: Your Google OAuth Client Secret
   - Sites: Add your site from the available sites

## Testing Your Integration

1. Go to your login or signup page
2. Click the "Sign up with Google" button
3. You should be redirected to Google's authentication page
4. After authenticating with Google:
   - If the email exists, you'll be redirected to login page
   - If it's a new user, you'll be taken to the role selection page

## Troubleshooting

- If you get redirect URI mismatch errors, double-check that your URIs in Google Cloud Console match exactly with what django-allauth is using
- Clear your browser cookies if testing multiple times
- Check the Django debug logs for detailed error information
- Make sure your SITE_ID and Site configurations in Django admin are correct 