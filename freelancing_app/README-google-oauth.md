# Google OAuth2 Setup for Freelancing App

This document provides instructions for setting up Google OAuth2 authentication in the Freelancing App.

## Google OAuth2 Integration Setup

### 1. Create Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" and select "OAuth client ID"
5. Choose "Web application" as the application type
6. Set the following:
   - Name: "Freelancing App" (or your preferred name)
   - Authorized JavaScript origins: `http://localhost:8000` (and your production URL)
   - Authorized redirect URIs: 
     - `http://localhost:8000/accounts/google/login/callback/`
     - `http://localhost:8000/accounts/google/login/callback`
     - (Add your production URLs as well)
7. Click "Create" and note down your "Client ID" and "Client Secret"

### 2. Configure Django Allauth

1. In the Django Admin site (`http://localhost:8000/admin/`), navigate to "Sites" and update the default site domain to match your domain (e.g., `localhost:8000` for local development)

2. Navigate to "Social Applications" in the admin site
3. Click "Add Social Application"
4. Fill in the details:
   - Provider: Select "Google"
   - Name: "Google"
   - Client ID: Your Google OAuth Client ID
   - Secret key: Your Google OAuth Client Secret
   - Key: Leave this blank
   - Sites: Add your site from the available sites

### 3. Flow Description

The Google OAuth2 implementation follows this flow:

1. User clicks "Sign up with Google" button
2. User is redirected to Google's authentication page
3. After successful authentication with Google:
   - If the user's email already exists in the system, they are redirected to the login page
   - If the user is new, they are redirected to the role selection page
4. After selecting a role (client or freelancer):
   - A new user account is created with the selected role
   - The user is redirected to the login page to log in

## Troubleshooting

### Common Issues

1. **Redirect URI Mismatch**: Make sure the redirect URIs in your Google Cloud Console match the ones used by django-allauth.
   
2. **Site Configuration**: Ensure your site domain is properly configured in the Django admin.

3. **Session Issues**: If users are losing session data during the OAuth flow, check your session configuration in settings.py.

4. **CSRF Errors**: If you encounter CSRF errors, ensure your CSRF middleware is properly configured.

### Testing

To test the Google OAuth flow:

1. Start your development server
2. Try signing up with Google
3. Verify that you are redirected correctly based on whether your email exists or not
4. Check that user accounts are created properly with the selected role 