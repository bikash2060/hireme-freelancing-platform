from django.shortcuts import redirect

def redirect_to_role_selection(request, sociallogin, **kwargs):
    """Redirect user to select role before saving the account"""
    if not sociallogin.is_existing:
        # Store user details in session temporarily
        request.session['socialaccount_data'] = {
            'email': sociallogin.account.extra_data.get('email', ''),
            'username': sociallogin.account.extra_data.get('name', ''),
            'provider': sociallogin.account.provider
        }
        return redirect('account:roles')  
    return None
