# Google OAuth Authentication Flow

## Overview

This document explains the authentication flow when a user logs in or registers using Google OAuth in our application. The system is designed to maintain clear separation between traditional (email/password) and Google OAuth authentication methods.

## Flow Diagram

```
┌───────────────┐     ┌────────────────────┐     ┌──────────────────┐
│  User clicks  │     │  Google Auth Page  │     │ CustomSocialAcct │
│ Login with    │────▶│  User authenticates│────▶│     Adapter      │
│   Google      │     │  with Google       │     │ pre_social_login │
└───────────────┘     └────────────────────┘     └────────┬─────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  Check if user  │
                                                 │    exists?      │
                                                 └────────┬────────┘
                                                          │
                         ┌─────────────────┐             │              ┌─────────────────┐
                         │    User has     │    Yes      │      No      │ Store OAuth     │
                         │ traditional     │◀────────────┼─────────────▶│ data in session │
                         │   account?      │             │              │                 │
                         └────────┬────────┘             │              └────────┬────────┘
                                  │                      │                       │
                                  │                      │                       │
                                  ▼                      ▼                       ▼
                         ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                         │  Redirect to    │    │ Complete normal │    │  Redirect to    │
                         │  login page     │    │  OAuth login    │    │  role selection │
                         │  with message   │    │                 │    │                 │
                         └─────────────────┘    └─────────────────┘    └────────┬────────┘
                                                                                │
                                                                                │
                                                                                ▼
                                                                      ┌─────────────────┐
                                                                      │  User selects   │
                                                                      │     role        │
                                                                      └────────┬────────┘
                                                                               │
                                                                               │
                                                                               ▼
                                                                      ┌─────────────────┐
                                                                      │ Create new user │
                                                                      │ auth_method=    │
                                                                      │   'google'      │
                                                                      └────────┬────────┘
                                                                               │
                                                                               │
                                                                               ▼
                                                                      ┌─────────────────┐
                                                                      │  Login user &   │
                                                                      │  redirect to    │
                                                                      │   home page     │
                                                                      └─────────────────┘
```

## Authentication Flow

### 1. Initial OAuth Process
- User clicks "Login with Google" button
- The user is redirected to Google's authentication page
- After authenticating with Google, the flow is intercepted by the `CustomSocialAccountAdapter.pre_social_login` method

### 2. Pre-social Login Handling (accounts/adapters.py)
```python
def pre_social_login(self, request, sociallogin):
    # Store current date in session
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

### 3. Branching Logic

#### 3.1 For Existing Users
- If the email already exists in our database, we check the `auth_method` field:
  - If `auth_method == 'traditional'`: User is redirected to login page with a message to use password login instead
  - If `auth_method == 'google'`: The normal social login flow continues, logging the user in

#### 3.2 For New Users
- For new users, we store the OAuth data in the session
- Redirect to `OAuthRoleSelectionView` to let the user select a role (client or freelancer)

### 4. Role Selection for New Users (OAuthRoleSelectionView)
- User selects role (client or freelancer)
- On form submission, the application:
  1. Deserializes the saved OAuth data
  2. Creates a new user with `auth_method='google'`
  3. Assigns random password (since login will be via Google)
  4. Downloads and saves profile picture from Google (if available)
  5. Creates associated profile (Client or Freelancer) based on selected role
  6. Logs the user in and redirects to home page

### 5. Traditional Login Prevention
- In the `UserLoginView.post` method, we check if a user exists with `auth_method='google'`:
```python
google_user = User.objects.filter(email=email, auth_method='google').first()
if google_user:
    messages.error(request, 'This email is registered with Google. Please login with Google.')
    return render(request, self.login_template, {'form_data': login_data})
```
- This prevents users from attempting to log in with password if they registered via Google

### 6. Traditional Registration Prevention
- In `UserSignupView.post`, we check if a user already exists with the email:
```python
if User.objects.filter(email=email_address).exists():
    user = User.objects.get(email=email_address)
    # Check if registered with Google OAuth
    if user.auth_method == 'google':
        messages.error(request, 'This email is registered with Google. Please login with Google.')
        return redirect(self.login_url)
```
- This prevents users from creating a traditional account if they already have a Google account

## Data Model

The User model has an `auth_method` field to track how users registered:
```python
auth_method = models.CharField(max_length=20, choices=[
    ('traditional', 'Traditional'),
    ('google', 'Google')
], default='traditional')
```

## Security Considerations

1. Users can only use the authentication method they initially registered with
2. Clear separation between traditional and Google OAuth accounts
3. OAuth users are automatically verified (no OTP verification needed)
4. Random passwords are assigned to Google OAuth accounts for security

## Redundant User Existence Checks

Our application performs user existence checks in two places:

1. **In CustomSocialAccountAdapter (pre_social_login)**: 
   ```python
   try:
       user = User.objects.get(email=email)
       # If user exists with traditional auth
       if user.auth_method == 'traditional':
           messages.error(request, 'This email is already registered with password. Please login using your password.')
           raise ImmediateHttpResponse(redirect(reverse('account:login')))
   ```

2. **In OAuthRoleSelectionView.post**:
   ```python
   if User.objects.filter(email=email).exists():
       user = User.objects.get(email=email)
       # Check if the user was registered via traditional method
       if user.auth_method == 'traditional':
           messages.error(request, 'This email is already registered with password. Please login using your password.')
           return redirect(self.login_url)
   ```

### Why the redundancy?

This redundancy serves as a security measure and provides defense in depth:

1. **First Check (Adapter)**: Intercepts the OAuth flow immediately after Google authentication but before any session data is processed.

2. **Second Check (OAuthRoleSelectionView)**: Acts as a backup in case:
   - The adapter check was bypassed for any reason
   - A user account was created between the initial check and the role selection
   - The user tried to manipulate the session data

3. **Consistent User Experience**: Both checks provide the same error message, ensuring a consistent experience regardless of where the check is triggered.

This approach ensures that we maintain strict separation between traditional and Google authentication methods, even if there are unexpected issues with the primary check.

## Potential Future Improvements

1. **Account Linking**: Allow users to link their traditional account with their Google account, giving them the option to log in using either method.

2. **Multiple OAuth Providers**: Extend the authentication system to support additional OAuth providers (Facebook, Twitter, GitHub, etc.) using the same pattern.

3. **Session Security Enhancement**: Add additional security measures to prevent session manipulation between the adapter redirect and role selection page.

4. **Account Migration**: Provide a pathway for users to transition from traditional to OAuth authentication (or vice versa) with proper verification.

5. **Activity Logging**: Log authentication method changes and login attempts for better security monitoring and user support.

6. **Fallback Authentication**: In rare cases where OAuth provider is down, provide temporary access alternatives for critical user needs. 