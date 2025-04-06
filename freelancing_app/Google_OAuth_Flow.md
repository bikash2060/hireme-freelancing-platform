# Google OAuth Authentication Flow

This document explains how authentication works when users sign in with Google in our application. It includes all the steps and decision points in the process.

## Overview

The authentication flow is designed to:
1. Allow users to sign in with Google
2. Keep traditional and Google accounts separate
3. Require new Google users to select a role (client or freelancer)
4. Prevent cross-authentication methods

## Flow Diagram

```
+-----------------+      +-------------------+      +----------------+
| User clicks     |      | Google Login Page |      | Our Custom     |
| "Login with     | -->  | User enters their | -->  | Social Account |
| Google" button  |      | Google credentials|      | Adapter        |
+-----------------+      +-------------------+      +-------+--------+
                                                           |
                                                           v
                                                    +------+-------+
                                                    | Check if user|
                                                    | exists with  |
                                                    | this email   |
                                                    +------+-------+
                                                           |
                           +------------------------+      |      +------------------------+
                           |                        |      |      |                        |
                           v                        |      |      v                        v
                +----------+-----------+            |      |   +--+---------------------+  |
                | User exists with     |<-----------+------+-->| User exists with      |  |
                | traditional account? |    Yes            No  | Google account?       |  |
                +----------+-----------+                       +--+---------------------+  |
                           |                                      |                        |
                           v                                      v                        v
                +----------+-----------+            +-------------+------------+  +--------+---------+
                | Redirect to login    |            | Complete normal login    |  | Redirect to role |
                | page with message to |            | flow with Google account |  | selection page   |
                | use password         |            +--------------------------|  +--------+---------+
                +----------------------+                                                   |
                                                                                          v
                                                                              +-----------+----------+
                                                                              | User selects role    |
                                                                              | (client/freelancer)  |
                                                                              +-----------+----------+
                                                                                          |
                                                                                          v
                                                                              +-----------+----------+
                                                                              | Create new user with |
                                                                              | auth_method='google' |
                                                                              +-----------+----------+
                                                                                          |
                                                                                          v
                                                                              +-----------+----------+
                                                                              | Create role profile   |
                                                                              | (Client/Freelancer)   |
                                                                              +-----------+----------+
                                                                                          |
                                                                                          v
                                                                              +-----------+----------+
                                                                              | Login user and       |
                                                                              | redirect to home     |
                                                                              +----------------------+
```

## Step-by-Step Flow

### 1. User Initiates Google Login

The process begins when a user clicks the "Login with Google" button on the login page. This directs them to Google's authentication page.

### 2. Google Authentication

Google handles the authentication and verifies the user's identity. After successful authentication, Google redirects back to our application with the user information.

### 3. CustomSocialAccountAdapter Intercepts

When Google redirects back, our `CustomSocialAccountAdapter.pre_social_login` method intercepts the callback:

```python
def pre_social_login(self, request, sociallogin):
    # Store timestamp
    request.session['oauth_timestamp'] = timezone.now().isoformat()
    
    # Get email from the social account data
    email = sociallogin.account.extra_data.get('email')
    
    # Check if user exists in our database
    try:
        user = User.objects.get(email=email)
        # If user exists with traditional auth
        if user.auth_method == 'traditional':
            messages.error(request, 'This email is already registered with password. Please login using your password.')
            raise ImmediateHttpResponse(redirect(reverse('account:login')))
        
        # If user exists with OAuth - let the normal login flow continue
        return
        
    except User.DoesNotExist:
        # New user - store data in session and redirect to role selection
        request.session['sociallogin_provider'] = sociallogin.account.provider
        request.session['sociallogin_email'] = email
        request.session['sociallogin'] = sociallogin.serialize()
        raise ImmediateHttpResponse(redirect(reverse('account:oauth_role_selection')))
```

### 4. Branch Based on User Existence

The flow branches into three paths based on the user's existence:

#### 4.1 User Exists with Traditional Authentication

If a user with the same email already exists and has `auth_method='traditional'`:
- An error message is shown: "This email is already registered with password. Please login using your password."
- The user is redirected to the login page
- Login is prevented

#### 4.2 User Exists with Google Authentication

If a user with the same email already exists and has `auth_method='google'`:
- The normal OAuth login flow continues
- The user is logged in automatically
- They are redirected to the home page

#### 4.3 New User (No Account Exists)

If no user with the provided email exists:
- The OAuth data is stored in the session
- The user is redirected to the role selection page

### 5. Role Selection for New Users

For new users, the OAuthRoleSelectionView shows a page to select their role:

```python
def get(self, request):
    # Verify the user came from OAuth flow
    if not request.session.get('sociallogin'):
        messages.error(request, 'Invalid request.')
        return redirect(self.login_url)
    
    email = request.session.get('sociallogin_email')
    if not email:
        messages.error(request, 'Email information missing.')
        return redirect(self.login_url)
    
    return render(request, self.role_selection_template, {'email': email})
```

### 6. Creating a New User with Google Auth

When the user selects a role and submits the form, the post method processes it:

```python
def post(self, request):
    # Get stored OAuth data
    serialized_sociallogin = request.session.get('sociallogin')
    if not serialized_sociallogin:
        messages.error(request, 'Invalid request.')
        return redirect(self.login_url)
    
    # Get the role from the form
    role = request.POST.get('role')
    if not role or role not in ['client', 'freelancer']:
        messages.error(request, 'Please select a valid role.')
        return render(request, self.role_selection_template, {
            'email': request.session.get('sociallogin_email')
        })
    
    # Deserialize the sociallogin object
    sociallogin = SocialLogin.deserialize(serialized_sociallogin)
    
    # Get email and user data from social account
    email = sociallogin.account.extra_data.get('email')
    full_name = sociallogin.account.extra_data.get('name', '')
    
    # Double-check if a user was created in the meantime
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        if user.auth_method == 'traditional':
            messages.error(request, 'This email is already registered with password. Please login using your password.')
            return redirect(self.login_url)
        # Otherwise, let them log in with the existing Google account
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect(self.home_url)
    
    # Create a username from the email
    username = email.split('@')[0]
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    # Create the user
    user = User.objects.create(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        is_verified=True,  # OAuth users are verified by default
        auth_method='google'
    )
    
    # Set a random password
    random_password = str(uuid.uuid4())
    user.set_password(random_password)
    
    # Save profile picture if available
    profile_picture_url = sociallogin.account.extra_data.get('picture')
    if profile_picture_url:
        # Download and save profile picture...
    
    user.save()
    
    # Create role-specific profile
    if role == 'client':
        Client.objects.create(user=user)
    elif role == 'freelancer':
        Freelancer.objects.create(user=user)
    
    # Connect social account to user
    SocialAccount.objects.create(
        user=user,
        provider=sociallogin.account.provider,
        uid=sociallogin.account.uid,
        extra_data=sociallogin.account.extra_data
    )
    
    # Log the user in
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    # Clean up session
    for key in ['sociallogin', 'sociallogin_email', 'sociallogin_provider', 'oauth_timestamp']:
        if key in request.session:
            del request.session[key]
    
    messages.success(request, 'You have successfully logged in.')
    return redirect(self.home_url)
```

## Preventing Cross-Authentication

Our system prevents users from using the wrong authentication method:

### 1. When Using Traditional Login with Google Email

In the `UserLoginView.post` method, we check if a user is trying to use password login for a Google account:

```python
def post(self, request):
    email = request.POST.get('emailaddress', '').strip().lower()
    password = request.POST.get('password', '').strip()
    
    # Validate login form
    valid, error_message = validate_login_form(email, password)
    if not valid:
        messages.error(request, error_message)
        return render(request, self.login_template, {'form_data': {'email': email}})
    
    # Check if user exists with Google auth
    google_user = User.objects.filter(email=email, auth_method='google').first()
    if google_user:
        messages.error(request, 'This email is registered with Google. Please login with Google.')
        return render(request, self.login_template, {'form_data': {'email': email}})
    
    # Continue with traditional login...
```

### 2. When Trying to Register with Existing Google Email

In the `UserSignupView.post` method, we check if someone tries to register traditionally with an email that's already used for Google auth:

```python
def post(self, request):
    email_address = request.POST.get('emailaddress').strip().lower()
    
    # Check if user already exists
    if User.objects.filter(email=email_address).exists():
        user = User.objects.get(email=email_address)
        # Check if registered with Google OAuth
        if user.auth_method == 'google':
            messages.error(request, 'This email is registered with Google. Please login with Google.')
            return redirect(self.login_url)
        else:
            messages.error(request, 'This email is already registered. Please use a different email.')
            return render(request, self.signup_template, {'form_data': signup_data})
    
    # Continue with registration...
```

## User Model

The User model includes an `auth_method` field to track the authentication method:

```python
class User(AbstractBaseUser, PermissionsMixin):
    # ... other fields
    auth_method = models.CharField(max_length=20, choices=[
        ('traditional', 'Traditional'),
        ('google', 'Google')
    ], default='traditional')
    # ... other fields
```

## Security Considerations

1. **Separate Authentication Methods**: Users can only log in using the method they originally signed up with, preventing confusion and potential security issues.

2. **Random Password for OAuth Users**: Google OAuth users receive a random, very secure password that they never see or use.

3. **Double Checking**: User existence is checked both in the adapter and in the role selection view to handle race conditions or session manipulation.

4. **Session Expiry**: OAuth session data has a timeout to prevent stale authentication attempts.

5. **Automatic Verification**: Google OAuth users are automatically verified since Google has already verified their email.

## Common User Journeys

### New User with Google

1. User clicks "Login with Google"
2. Google authentication completes
3. User is redirected to role selection page
4. User selects role (client/freelancer)
5. New account is created with `auth_method='google'`
6. User is logged in and redirected to home page

### Existing Google User Login

1. User clicks "Login with Google"
2. Google authentication completes
3. System recognizes existing Google account
4. User is automatically logged in
5. User is redirected to home page

### Traditional User Tries Google Login

1. User clicks "Login with Google"
2. Google authentication completes
3. System detects email is registered with traditional method
4. User sees error: "This email is already registered with password. Please login using your password."
5. User is redirected to login page

### Google User Tries Traditional Login

1. User enters email and password on login form
2. System detects email is registered with Google
3. User sees error: "This email is registered with Google. Please login with Google."
4. User must use Google login button instead 